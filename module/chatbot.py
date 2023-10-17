import json
import pickle
import os
import numpy as np
import threading
import onnxruntime as ort
import random
from tokenizers import Tokenizer


class Chatbot:

    def __init__(self):
        self.is_running = False
        self.lock = threading.Lock()

        self.VOCAB_SIZE = 3000
        self.TOKENS = {
                    "start_of_message": "[SOM]",
                    "end_of_message": "[EOM]",
                    "padding": "[PAD]",
                    "newline": "[NEWLINE]",
                    }
        
        self.num_layers = 3
        self.emb_dim = 128
        self.hidden_size = 128


        self.chatbot = ort.InferenceSession("data/chatbot_model.onnx")
        self.tokenizer = Tokenizer.from_file("data/tokenizer.json")
        self.som_token_index = self.tokenizer.token_to_id(self.TOKENS["start_of_message"])
        self.eom_token_index = self.tokenizer.token_to_id(self.TOKENS["end_of_message"])

        self.hidden_state = np.zeros((self.num_layers, 1, self.hidden_size)).astype(np.float32)
        self.cell_state = np.zeros((self.num_layers, 1, self.hidden_size)).astype(np.float32)

    def reset_hidden(self):
        self.hidden_state = np.zeros((self.num_layers, 1, self.hidden_size)).astype(np.float32)
        self.cell_state = np.zeros((self.num_layers, 1, self.hidden_size)).astype(np.float32)

    def check_if_running(self):
        return self.is_running

    def run(self, prompt, n_tokens_to_generate=50):

        with self.lock:
            if self.is_running:
                return
            self.is_running = True

        input = np.array(self.tokenizer.encode(prompt).ids).reshape(1, -1)
        output_list = []

        for i in range(n_tokens_to_generate):

            ort_inputs = {
                "input_tokens": input.astype(np.int64),
                "hidden_state_in": self.hidden_state,
                "cell_state_in": self.cell_state
            }
            ort_outputs = self.chatbot.run(None, ort_inputs)
            input = np.argmax(ort_outputs[0], axis=1).reshape(-1, 1)
            output_list.append(int(input[0][0]))
            self.hidden_state = ort_outputs[1]
            self.cell_state = ort_outputs[2]

            if input[0][0] == self.eom_token_index:
                break

        generated_message = self.tokenizer.decode(output_list)
        generated_message = generated_message.replace(self.TOKENS["start_of_message"], "")
        generated_message = generated_message.replace(self.TOKENS["end_of_message"], "")
        generated_message = generated_message.replace(self.TOKENS["newline"], "\n")

        if generated_message.replace("\n", "") == "":
            generated_message = "[EMPTY GENERATION]"

        with self.lock:
            self.is_running = False

        return generated_message

        
