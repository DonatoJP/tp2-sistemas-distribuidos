import json
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from ..operator import AbstractOperator

class SentimentAnalysisOperator(AbstractOperator):
    def __init__(self, column, **kwargs) -> None:
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.column = column
        super().__init__(**kwargs)
    
    def _calc_sentiment(self, data: dict):
        value = self.sentiment_analyzer.polarity_scores(data[self.column])
        if value['compound'] <= 0:
            return 0
        
        return 1

    def exec_operation(self, data) -> list:
        def operation(data):
            result = {}
            data_dict = json.loads(data)
            result["result"] = self._calc_sentiment(data_dict)
            return (json.dumps(result), self.get_affinity(result))

        res = [ operation(x) for x in data ]
        return self._group_by_ak(res)
    
