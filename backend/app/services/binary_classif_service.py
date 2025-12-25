from typing import Dict
import joblib


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
    
    def predict(self, text: str, threshold: float = None) -> Dict:
        """
        Предсказывает, является ли текст проблемой
        
        ВАЖНО: Не делаем предобработку, так как она уже встроена в Pipeline!
        Pipeline сам делает: текстовую предобработку → TF-IDF → классификацию
        """
        if threshold is None:
            threshold = self.threshold
            
        result = {
            "is_problem": False,
            "probability": 0.0,
            "confidence": 0.0,
            "prediction_label": "Не проблема",
            "raw_text": text[:100] + "..." if len(text) > 100 else text  # Для отладки
        }
        
        if not text or not text.strip():
            return result
            
        try:
            # ВАЖНО: Pipeline ожидает сырой текст!
            # Он сам вызовет TfidfVectorizer, который сделает свою предобработку
            
            # Получаем вероятности
            proba = self.model.predict_proba([text])[0]
            
            # Предполагаем, что классы: [0, 1] где 1 = "Проблема"
            # Проверим порядок классов
            classes = self.model.named_steps['clf'].classes_
            if len(classes) == 2:
                # Находим индекс класса "Проблема" (скорее всего 1)
                problem_class_index = 1 if classes[1] == 1 else 0
                problem_prob = proba[problem_class_index]
            else:
                problem_prob = proba[1] if len(proba) > 1 else proba[0]
            
            # Классификация по порогу
            prediction = 1 if problem_prob >= threshold else 0
            
            # Заполняем результат
            result["is_problem"] = bool(prediction)
            result["probability"] = float(problem_prob)
            result["confidence"] = abs(problem_prob - 0.5) * 2
            result["prediction_label"] = "Проблема" if prediction == 1 else "Не проблема"
            
            # Для отладки: посмотрим, как Pipeline обработал текст
            print(f"Текст: {text[:50]}...")
            print(f"Вероятность проблемы: {problem_prob:.4f}")
            print(f"Предсказание: {result['prediction_label']}")
            
        except Exception as e:
            print(f"Ошибка при предсказании: {e}")
            import traceback
            traceback.print_exc()
            
        return result
    
    def get_top_features(self, text: str, top_n: int = 10) -> Dict:
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
            if not hasattr(self.model.named_steps['clf'], 'coef_'):
                print("Модель не имеет коэффициентов для анализа признаков")
                return result
            
            # Получаем векторизатор и классификатор из Pipeline
            vectorizer = self.model.named_steps['tfidf']
            classifier = self.model.named_steps['clf']
            
            # Преобразуем текст в вектор (так же, как при предсказании)
            text_vec = vectorizer.transform([text])
            
            # Получаем имена признаков и коэффициенты
            feature_names = vectorizer.get_feature_names_out()
            coefficients = classifier.coef_[0]
            
            # Находим ненулевые признаки в тексте
            nonzero_indices = text_vec.nonzero()[1]
            
            # Собираем признаки
            text_features = []
            for idx in nonzero_indices:
                feature_name = feature_names[idx]
                weight = coefficients[idx]
                tfidf_value = text_vec[0, idx]
                importance = tfidf_value * weight
                
                text_features.append({
                    'feature': feature_name,
                    'weight': float(weight),
                    'importance': float(importance),
                    'tfidf_value': float(tfidf_value)
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
            import traceback
            traceback.print_exc()
            
        return result

# Создаем глобальный экземпляр
binary_classification_service = BinaryClassificationService()