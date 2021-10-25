import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from ..operator import AbstractOperator

class SentimentAnalysisOperator(AbstractOperator):
    def __init__(self) -> None:
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        super().__init__()
    
    def _calc_sentiment(self, data: dict, column: str):
        value = self.sentiment_analyzer.polarity_scores(data[column])
        if value['compound'] <= 0:
            return 0
        
        return 1

    def exec_operation(self, data, **kwargs) -> list:
        result = {}
        data_dict = json.loads(data)
        result["result"] = self._calc_sentiment(data_dict, **kwargs)
        return [ json.dumps(result) ]
    
