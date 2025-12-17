import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

PROMPT = [
    {"role": "system", "content": "You are an AI assistant that helps organize"
     " information from a handwritten document. The information you get from"
     " the user is extracted poorly, but it has the context of from a farm-"
     " related document. Your task is to help the user fix incorrectly digitized"
     " information and organize it in a structured format."},
    {"role": "user", "content": "Can you switch mis-translated words with"
     " appropriate farm-related vocabulary in this information and convert it into JSON"
     " format? Here is the information: "},

]


class Phi3Wrapper:
    """
    Wrapper class for the Phi-3 language model.

    Interface:
    initialize it then call generate() with messages in the format described below.
    """

    def __init__(self):
        torch.random.manual_seed(0)
        self.model = AutoModelForCausalLM.from_pretrained(
            "microsoft/Phi-3-mini-128k-instruct",
            device_map="cpu",  # use GPU once integrated into the devcontainer
            torch_dtype="auto",
            trust_remote_code=True,
        )

        self.tokenizer = AutoTokenizer.from_pretrained(
            "microsoft/Phi-3-mini-128k-instruct")

        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
        )

        # TODO: tune these parameters
        self.generation_args = {
            "max_new_tokens": 500,
            "return_full_text": False,
            "temperature": 0.0,
            "do_sample": False,
        }

    def generate(self, messages):
        """
        Generate a response from the Phi-3 model based on the provided messages.

        messages are in the format of:
        [
            {"role": "system", "content": "..."},
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."},
            ...
        ]
        """
        output = self.pipe(messages, **self.generation_args)
        return output[0]['generated_text']

    def clean_ocr_output(self, ocr_output: list) -> str:
        """
        Clean the OCR output of handwritten text recognition with the Phi-3 
        model to correct words to be farm-related and organized.

        Args:
            ocr_output (list): The raw OCR output as a list of results.

        Returns:
            str: The cleaned text extracted from the OCR output in JSON format.
        """
        messages = PROMPT + [
            {"role": "user", "content": str(ocr_output)}
        ]
        return self.generate(messages)


if __name__ == "__main__":
    llm = Phi3Wrapper()
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Can you provide ways to eat combinations of bananas and dragonfruits?"},
        {"role": "assistant", "content": "Sure! Here are some ways to eat bananas and dragonfruits together: 1. Banana and dragonfruit smoothie: Blend bananas and dragonfruits together with some milk and honey. 2. Banana and dragonfruit salad: Mix sliced bananas and dragonfruits together with some lemon juice and honey."},
        {"role": "user", "content": "What about solving an 2x + 3 = 7 equation?"},
    ]
    output = llm.generate(messages)
    print(output)
