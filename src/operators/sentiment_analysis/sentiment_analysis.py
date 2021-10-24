from nltk.sentiment.vader import SentimentIntensityAnalyzer
from ..operator import AbstractOperator

class SentimentAnalysisOperator(AbstractOperator):
    def __init__(self) -> None:
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        super().__init__()
    
    def _calc_sentiment(self, line: str):
        value = self.sentiment_analyzer.polarity_scores(line)
        if value['compound'] <= 0:
            return 0
        
        return 1

    def exec_operation(self, data, **kwargs) -> list:
        result = self._calc_sentiment(data)
        return [ str(result) ]
    
