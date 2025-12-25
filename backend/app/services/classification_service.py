import pickle
from typing import Dict, List


class ClassificationService:
    """Сервис для классификации текстов"""

    def __init__(
        self,
        model_path: str = "/home/saryglar311/Projects/DIPLOM/backend/app/ml/LR/logistic_regression_model_topics.pkl",
    ):
        self.model = None
        self.vectorizer = None
        self.topics = None
        self.morph = None
        self.stopwords = None
        self._load_model(model_path)
        
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
        
        self.topic_thresholds = {
            'environment': 0.4,
            'manufacture': 0.4,
            'employment': 0.3,
            'financesandcredit': 0.4,
            'homeandinfrastructure': 0.5,
            'healthservice': 0.4,
            'educationandsport': 0.4,
            'socialsphere': 0.6,
            'politics': 0.5,
            'criminality': 0.6,
            'demographic': 0.3
        }

    def _load_model(self, model_path: str):
        """Загружает модель классификации"""
        try:
            with open(model_path, "rb") as f:
                saved_data = pickle.load(f)
                self.model = saved_data["model"]
                self.vectorizer = saved_data["vectorizer"]
                self.topics = saved_data["topics"]
                
                if "stopwords" in saved_data:
                    self.stopwords = set(saved_data["stopwords"])
                    print(f"Загружено {len(self.stopwords)} стоп-слов из модели")
                else:
                    import nltk
                    nltk.download("stopwords", quiet=True)
                    from nltk.corpus import stopwords
                    self.stopwords = set(stopwords.words("russian"))
                    print(f"Загружено {len(self.stopwords)} стандартных стоп-слов")
            
            print(f"Модель загружена. Темы: {self.topics}")
            print(f"Размер словаря векторизатора: {len(self.vectorizer.vocabulary_)}")
            
        except Exception as e:
            print(f"Ошибка загрузки модели: {e}")
            raise

    def preprocess_text_simple(self, text: str) -> str:
        """
        Упрощённая предобработка текста
        Векторизатор обучен на лемматизированных текстах, 
        но передаём сырой текст - он справится
        """
        if not text:
            return ""
        
        text = text.lower()
        
        text = ' '.join(text.split())
        
        return text

    def predict_topics(self, text: str) -> List[str]:
        """Предсказывает темы для текста (с порогами как при обучении)"""
        if not text or not text.strip():
            return ['unclassified']

        try:
            processed_text = self.preprocess_text_simple(text)
            
            if not processed_text:
                return ['unclassified']
            
            text_vec = self.vectorizer.transform([processed_text])
            
            predicted_topics = []
            
            for i, (topic, estimator) in enumerate(zip(self.topics, self.model.estimators_)):
                prob = estimator.predict_proba(text_vec)[0, 1]
                
                threshold = self.topic_thresholds.get(topic, 0.3)
                
                if prob > threshold:
                    if topic in self.topic_mapping:
                        predicted_topics.append(self.topic_mapping[topic])
                    else:
                        predicted_topics.append(topic)
            
            if not predicted_topics:
                return ['unclassified']
            
            return predicted_topics

        except Exception as e:
            print(f"Ошибка при предсказании тем: {e}")
            return ['unclassified']

    def predict_topics_with_probs(self, text: str) -> Dict:
        """Предсказывает темы с вероятностями"""
        result = {
            "topics": [],
            "probabilities": {},
            "confidence": 0.0,
        }

        if not text or not text.strip():
            return result

        try:
            processed_text = self.preprocess_text_simple(text)
            
            if not processed_text:
                return result
            
            text_vec = self.vectorizer.transform([processed_text])
            
            probabilities = []
            
            for i, (topic, estimator) in enumerate(zip(self.topics, self.model.estimators_)):
                prob = estimator.predict_proba(text_vec)[0, 1]
                result["probabilities"][topic] = float(prob)
                probabilities.append(prob)
                
                threshold = self.topic_thresholds.get(topic, 0.3)
                if prob > threshold:
                    if topic in self.topic_mapping:
                        result["topics"].append(self.topic_mapping[topic])
                    else:
                        result["topics"].append(topic)
            
            if probabilities:
                result["confidence"] = sum(probabilities) / len(probabilities)

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