
import json

notebook_path = r"c:/Users/nahue/Documents/Ceia/NLP/Proyectos_NLP/desafio_4.ipynb"

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

# Code to insert
inference_models_code = [
    "# Inferencia: Modelos Encoder y Decoder\n",
    "encoder_model = Model(encoder_inputs, encoder_states)\n",
    "\n",
    "decoder_state_input_h = Input(shape=(n_units,))\n",
    "decoder_state_input_c = Input(shape=(n_units,))\n",
    "decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]\n",
    "\n",
    "decoder_inputs_single = Input(shape=(1,))\n",
    "decoder_inputs_single_x = decoder_embedding_layer(decoder_inputs_single)\n",
    "\n",
    "decoder_outputs, state_h, state_c = decoder_lstm(decoder_inputs_single_x, initial_state=decoder_states_inputs)\n",
    "decoder_states = [state_h, state_c]\n",
    "decoder_outputs = decoder_dense(decoder_outputs)\n",
    "\n",
    "decoder_model = Model([decoder_inputs_single] + decoder_states_inputs, [decoder_outputs] + decoder_states)\n",
    "\n"
]

# Find the cell with translate_sentence
modified = False
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = cell['source']
        # Check if the cell defines translate_sentence
        if any("def translate_sentence(input_seq):" in line for line in source):
            # Prepend the inference model definitions
            cell['source'] = inference_models_code + source
            modified = True
            print("Found and modified the translate_sentence cell.")
            break

if modified:
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=1)
    print("Notebook saved successfully.")
else:
    print("Could not find the target cell.")
