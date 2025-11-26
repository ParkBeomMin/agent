from crewai.tools import tool

# """ """ 를 doc string이라고 하는데, 함수가 무슨 일을 하는지 설명해주는 문자열임. crew ai가 이 doc string을 읽어서 function의 schema를 생성함.
@tool
def count_letters(sentence: str) -> int:
    """ 
    This function is to count the amount of letters in a sentence. 
    The input is a 'sentence' string, and the output is an integer.
    """
    return len(sentence) 