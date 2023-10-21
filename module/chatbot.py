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
                    }
        
        self.num_layers = 3
        self.emb_dim = 512
        self.hidden_size = 512
        self.temperature = 0.7


        self.chatbot = ort.InferenceSession("data/chatbot_lstm_model.onnx")
        self.tokenizer = Tokenizer.from_file("data/tokenizer.json")
        self.som_token_index = int(self.tokenizer.token_to_id(self.TOKENS["start_of_message"]))
        self.eom_token_index = int(self.tokenizer.token_to_id(self.TOKENS["end_of_message"]))

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
        try:
            input_tokens = np.array(self.tokenizer.encode(prompt).ids).astype(np.int64).reshape(1, -1)
            output_list = []

            for i in range(n_tokens_to_generate):

                ort_inputs = {
                    "input_tokens": input_tokens,
                    "hidden_state_in": self.hidden_state,
                    "cell_state_in": self.cell_state
                }
                ort_outputs = self.chatbot.run(None, ort_inputs)
                logits = ort_outputs[0][0][-1]
                logits = logits / self.temperature
                exp_logits = np.exp(logits - np.max(logits))
                logits_sum = np.sum(exp_logits)
                probs = exp_logits / logits_sum
                input_tokens = np.random.choice(range(self.VOCAB_SIZE), p=probs).astype(np.int64).reshape(1, 1)

                output_list.append(int(input_tokens[0][0]))
                self.hidden_state = ort_outputs[1]
                self.cell_state = ort_outputs[2]

                if output_list[-1] == self.eom_token_index:
                    break
                if i == 49:
                    output_list[-1] = self.eom_token_index
                    break
            

            #feed EOM token back into model
            ort_inputs = {
                "input_tokens": np.array(self.eom_token_index).astype(np.int64).reshape(1, 1),
                "hidden_state_in": self.hidden_state,
                "cell_state_in": self.cell_state
            }
            ort_outputs = self.chatbot.run(None, ort_inputs)
            self.hidden_state = ort_outputs[1]
            self.cell_state = ort_outputs[2]


            generated_message = self.tokenizer.decode(output_list)
            generated_message = generated_message.replace(self.TOKENS["start_of_message"], "")
            generated_message = generated_message.replace(self.TOKENS["end_of_message"], "")
            generated_message = generated_message.replace(self.TOKENS["padding"], "")

            if generated_message.replace("\n", "").strip(" ") == "":
                generated_message = "[EMPTY GENERATION]"

        except Exception as e:
            generated_message = "[ERROR GENERATING RESPONSE]"
            print(f"ERROR in chatbot: {e}")

        with self.lock:
            self.is_running = False

        return generated_message

        
