from typing import Dict, Optional, Any
import joblib
import traceback
import numpy as np


class BinaryClassificationService:
    """Сервис для бинарной классификации текстов (проблема/не проблема)"""
    
    def __init__(
        self,
        model_path: str = "/home/saryglar311/Projects/DIPLOM/backend/app/ml/LR/logistic_regression_model_neg.pkl",
    ):
        self.threshold = 0.5
        
        # Загружаем модель
        print(f"Загрузка модели из {model_path}")
        self.model = joblib.load(model_path)
        
        # Проверяем, что это Pipeline
        if not hasattr(self.model, 'named_steps'):
            raise ValueError("Загруженная модель не является Pipeline. Ожидается модель от GridSearchCV")
        
        print(f"Модель загружена. Тип: {type(self.model)}")
        print(f"Шаги пайплайна: {list(self.model.named_steps.keys())}")
        
        # Получаем классификатор для диагностики
        self.classifier = self.model.named_steps['clf']
        print(f"Классы классификатора: {self.classifier.classes_}")
    
    def _safe_predict_proba(self, text: str):
        """Безопасное получение вероятностей с обходом ошибки multi_class"""
        try:
            # Пробуем стандартный способ
            return self.model.predict_proba([text])[0]
        except AttributeError as e:
            if "'multi_class'" in str(e):
                print("Обнаружена ошибка с multi_class, используем обходной путь")
                
                # Обходной путь 1: Используем decision_function если доступен
                if hasattr(self.classifier, 'decision_function'):
                    try:
                        # Получаем текстовый вектор через TF-IDF
                        vectorizer = self.model.named_steps['tfidf']
                        text_vec = vectorizer.transform([text])
                        decision = self.classifier.decision_function(text_vec)[0]
                        
                        # Преобразуем decision function в вероятность
                        # Для бинарной классификации используем сигмоиду
                        prob = 1 / (1 + np.exp(-decision))
                        
                        if len(self.classifier.classes_) == 2:
                            # Для бинарной классификации
                            return np.array([1 - prob, prob])
                        else:
                            return np.array([prob])
                    except Exception as e:
                        print(f"Ошибка в decision_function: {e}")
                
                # Обходной путь 2: Используем predict и возвращаем бинарные вероятности
                prediction = self.model.predict([text])[0]
                
                if len(self.classifier.classes_) == 2:
                    # Для бинарной классификации
                    if prediction == 1:
                        return np.array([0.0, 1.0])
                    else:
                        return np.array([1.0, 0.0])
                else:
                    # Для многоклассовой
                    probs = np.zeros(len(self.classifier.classes_))
                    probs[prediction] = 1.0
                    return probs
            else:
                # Если это не ошибка multi_class, пробрасываем дальше
                raise
    
    def predict(self, text: str, threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Предсказывает, является ли текст проблемой
        """
        if threshold is None:
            threshold = self.threshold
            
        result = {
            "is_problem": False,
            "probability": 0.0,
            "confidence": 0.0,
            "prediction_label": "Не проблема",
            "error": None
        }
        
        if not text or not text.strip():
            return result
            
        try:
            # Используем безопасный метод получения вероятностей
            proba = self._safe_predict_proba(text)
            
            # Определяем вероятность для класса "Проблема"
            if len(proba) == 2:
                # Бинарная классификация: [вероятность класса 0, вероятность класса 1]
                # Предполагаем, что класс 1 = "Проблема"
                problem_prob = proba[1]
                problem_class_index = 1
            else:
                # Если только одна вероятность, используем её
                problem_prob = proba[0]
                problem_class_index = 0
            
            # Классификация по порогу
            prediction = problem_class_index if problem_prob >= threshold else (1 - problem_class_index)
            
            # Заполняем результат - ВАЖНО: конвертируем numpy типы в стандартные Python типы!
            result["is_problem"] = bool(prediction == problem_class_index)
            result["probability"] = float(problem_prob)  # Конвертируем np.float64 в float
            result["confidence"] = float(abs(problem_prob - 0.5) * 2)  # Конвертируем np.float64 в float
            result["prediction_label"] = "Проблема" if prediction == problem_class_index else "Не проблема"
            
            
        except Exception as e:
            error_msg = str(e)
            traceback.print_exc()
            
            # Если всё падает, используем простое предсказание
            try:
                prediction = self.model.predict([text])[0]
                result["is_problem"] = bool(prediction == 1)
                result["probability"] = 1.0 if result["is_problem"] else 0.0
                result["prediction_label"] = "Проблема" if result["is_problem"] else "Не проблема"
                result["error"] = f"Использовано простое предсказание после ошибки: {error_msg}"
            except:
                result["error"] = error_msg
            
        return result
    
    def get_top_features(self, text: str, top_n: int = 10) -> Dict[str, Any]:
        """
        Получает наиболее важные признаки для классификации текста
        """
        result = {
            "problem_features": [],
            "non_problem_features": [],
            "text": text
        }
        
        try:
            # Проверяем, что модель имеет нужные атрибуты
            if not hasattr(self.classifier, 'coef_'):
                return result
            
            # Получаем векторизатор
            vectorizer = self.model.named_steps['tfidf']
            
            # Преобразуем текст в вектор
            text_vec = vectorizer.transform([text])
            
            # Получаем имена признаков и коэффициенты
            feature_names = vectorizer.get_feature_names_out()
            coefficients = self.classifier.coef_[0]
            
            # Находим ненулевые признаки в тексте
            nonzero_indices = text_vec.nonzero()[1]
            
            # Собираем признаки - ВАЖНО: конвертируем numpy типы
            text_features = []
            for idx in nonzero_indices:
                feature_name = feature_names[idx]
                weight = coefficients[idx]
                tfidf_value = text_vec[0, idx]
                importance = tfidf_value * weight
                
                text_features.append({
                    'feature': feature_name,
                    'weight': float(weight),  # Конвертируем np.float64 в float
                    'importance': float(importance),  # Конвертируем np.float64 в float
                    'tfidf_value': float(tfidf_value)  # Конвертируем np.float64 в float
                })
            
            # Сортируем по абсолютной важности
            text_features.sort(key=lambda x: abs(x['importance']), reverse=True)
            
            # Разделяем на признаки проблемы и не-проблемы
            problem_features = [f for f in text_features if f['weight'] > 0]
            non_problem_features = [f for f in text_features if f['weight'] < 0]
            
            result['problem_features'] = problem_features[:top_n]
            result['non_problem_features'] = non_problem_features[:top_n]
            
            print(f"\nТоп-{top_n} признаков для текста:")
            print("Указывают на проблему:")
            for f in result['problem_features']:
                print(f"  {f['feature']}: вес={f['weight']:.4f}, важность={f['importance']:.4f}")
            
            print("\nУказывают на НЕ проблему:")
            for f in result['non_problem_features']:
                print(f"  {f['feature']}: вес={f['weight']:.4f}, важность={f['importance']:.4f}")
            
        except Exception as e:
            print(f"Ошибка при получении топ-признаков: {e}")
            traceback.print_exc()
            
        return result


# Создаем глобальный экземпляр
binary_classification_service = BinaryClassificationService()