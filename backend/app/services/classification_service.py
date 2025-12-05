import pickle
import re
from typing import Dict, List

import pymorphy3
from nltk.corpus import stopwords


class ClassificationService:
    """Сервис для классификации текстов с полной предобработкой"""

    def __init__(
        self,
        model_path: str = "/home/saryglar311/Projects/DIPLOM/backend/app/ml/LR/logistic_regression_model_russian.pkl",
    ):
        self.model = None
        self.vectorizer = None
        self.topics = None
        self.morph = None
        self.stopwords = None
        self._load_model(model_path)
        self._load_nlp_tools()

        self.topic_mapping = {
            'environment': 'environment',
            'manufacture': 'manufacture',
            'employment': 'employment',
            'financesandcredit': 'financesandcredit',
            'homeandinfrastructure': 'homeandinfrastructure',
            'healthservice': 'healthservice',
            'educationandsport': 'educationandsport',
            'socialsphere': 'socialsphere',
            'politics': 'politics',
            'criminality': 'criminality',
            'demographic': 'demographic',
            'unclassified': 'unclassified',
        }

    def _load_model(self, model_path: str):
        """Загружает модель классификации"""
        try:
            with open(model_path, "rb") as f:
                saved_data = pickle.load(f)
                self.model = saved_data["model"]
                self.vectorizer = saved_data["vectorizer"]
                self.topics = saved_data["topics"]
            print(f"Модель загружена. Темы: {self.topics}")
        except Exception as e:
            print(f"Ошибка загрузки модели: {e}")
            raise

    def _load_nlp_tools(self):
        """Загружает инструменты для предобработки текста"""
        try:
            # Лемматизатор для русского языка
            self.morph = pymorphy3.MorphAnalyzer()

            # Русские стоп-слова
            import nltk

            nltk.download("stopwords", quiet=True)
            self.stopwords = set(stopwords.words("russian"))

            # Дополнительные стоп-слова
            additional_stopwords = {
                "это",
                "вот",
                "ну",
                "же",
                "ли",
                "бы",
                "б",
                "ведь",
                "мол",
                "то",
                "таки",
                "как",
                "так",
                "вроде",
                "типа",
                "прямо",
                "просто",
                "сам",
                "сама",
                "сами",
                "само",
                "очень",
            }
            self.stopwords.update(additional_stopwords)

            print(f"Загружено {len(self.stopwords)} стоп-слов")

        except Exception as e:
            print(f"Ошибка загрузки NLP инструментов: {e}")
            self.morph = None
            self.stopwords = set()

    def preprocess_text(self, text: str) -> str:
        """Полная предобработка текста (как при обучении)"""
        if not text:
            return ""

        # 1. Привести к нижнему регистру
        text = text.lower()

        # 2. Удалить спецсимволы, оставить только буквы и цифры
        text = re.sub(r"[^\w\s]", " ", text)

        # 3. Удалить лишние пробелы
        text = re.sub(r"\s+", " ", text).strip()

        # 4. Токенизация
        words = text.split()

        # 5. Фильтрация и лемматизация
        processed_words = []
        for word in words:
            # Пропускаем короткие слова
            if len(word) < 2:
                continue

            # Пропускаем стоп-слова
            if word in self.stopwords:
                continue

            # Пропускаем числа
            if word.isdigit():
                continue

            # Лемматизация
            if self.morph:
                try:
                    parsed = self.morph.parse(word)[0]
                    lemma = parsed.normal_form
                    processed_words.append(lemma)
                except:
                    processed_words.append(word)
            else:
                processed_words.append(word)

        # 6. Собираем обратно в текст
        return " ".join(processed_words)

    def predict_topics(self, text: str, threshold: float = 0.3) -> List[str]:
        """Предсказывает темы для текста с полной предобработкой"""
        if not text or not text.strip():
            return []

        try:
            # ✅ ВАЖНО: Предобработка текста как при обучении!
            processed_text = self.preprocess_text(text)

            if not processed_text or len(processed_text.split()) < 2:
                # Если после обработки почти не осталось слов
                return []

            # Векторизация предобработанного текста
            text_vec = self.vectorizer.transform([processed_text])

            # Предсказание
            predictions = self.model.predict(text_vec)[0]

            # Получение тем
            predicted_topics = []
            for i, topic in enumerate(self.topics):
                if predictions[i] == 1:
                    # Маппим тему из модели в PostTopic
                    if topic in self.topic_mapping:
                        predicted_topics.append(self.topic_mapping[topic])
                    else:
                        predicted_topics.append(topic)
                        # Если ни одной темы не предсказано, возвращаем 'unclassified'
            if not predicted_topics:
                predicted_topics.append('unclassified')

            return predicted_topics

        except Exception as e:
            print(f"Ошибка при предсказании тем: {e}")
            return []

    def predict_topics_with_probs(self, text: str, threshold: float = 0.3) -> Dict:
        """Предсказывает темы с вероятностями"""
        result = {
            "topics": [],
            "probabilities": {},
            "processed_text": "",
            "confidence": 0.0,
        }

        if not text or not text.strip():
            return result

        try:
            # Предобработка
            processed_text = self.preprocess_text(text)
            result["processed_text"] = processed_text

            if not processed_text:
                return result

            # Векторизация
            text_vec = self.vectorizer.transform([processed_text])

            # Получаем вероятности для каждой темы
            total_prob = 0
            topic_count = 0

            for i, (topic, estimator) in enumerate(
                zip(self.topics, self.model.estimators_)
            ):
                prob = estimator.predict_proba(text_vec)[0, 1]
                result["probabilities"][topic] = float(prob)

                if prob > threshold:
                    result["topics"].append(topic)

                total_prob += prob
                topic_count += 1

            # Средняя уверенность
            if topic_count > 0:
                result["confidence"] = total_prob / topic_count

            return result

        except Exception as e:
            print(f"Ошибка при предсказании с вероятностями: {e}")
            return result

    def topics_to_string(self, topics: List[str]) -> str:
        """Преобразует список тем в строку для хранения в БД"""
        return ", ".join(topics) if topics else ""

    def string_to_topics(self, topics_str: str) -> List[str]:
        """Преобразует строку из БД обратно в список тем"""
        if not topics_str or not topics_str.strip():
            return []
        return [topic.strip() for topic in topics_str.split(",") if topic.strip()]


classification_service = ClassificationService()
