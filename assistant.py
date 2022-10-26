import torch

def answer_question(question, answer_text, tokenizer, model):
	"""
	We are going to pass the question dn the reference text in this function
	The function will return the answer and the confidence score
	You could also return the start span and end span,
	but it makes our work easier if we simply get the answer and the score

	"""

	input_ids = tokenizer.encode(question, answer_text)
	sep_index = input_ids.index(tokenizer.sep_token_id)
	num_seg_a = sep_index + 1

	# The remainder are segment B.
	num_seg_b = len(input_ids) - num_seg_a

	# Construct the list of 0s and 1s.
	segment_ids = [0] * num_seg_a + [1] * num_seg_b

	# There should be a segment_id for every input token.
	assert len(segment_ids) == len(input_ids)

	# ======== Evaluate ========
	# Run our example question through the model.
	start_scores, end_scores = model(torch.tensor([input_ids]),  # The tokens representing our input text.
									 token_type_ids=torch.tensor([segment_ids]),
									 return_dict=False)  # The segment IDs to differentiate question from answer_text
	START_SCORES = max(torch.sigmoid(start_scores).detach().numpy().tolist()[0])
	if START_SCORES > 0.10:

		answer_start = torch.argmax(start_scores)
		answer_end = torch.argmax(end_scores)

		# Get the string versions of the input tokens.
		tokens = tokenizer.convert_ids_to_tokens(input_ids)

		# Start with the first token.
		answer = tokens[answer_start]

		# Select the remaining answer tokens and join them with whitespace.
		for i in range(answer_start + 1, answer_end + 1):


			if tokens[i][0:2] == '##':
				answer += tokens[i][2:]


			else:
				answer += ' ' + tokens[i]

		return answer, START_SCORES
	else:
		return "NA", 0.00


text = """
My name is santosh. I had a sprint planning meeting on 10/19/2022 got EPU card assigned for the sprint work, I was assigned a total of 8 points and 3 strech points.
"""

if __name__ == '__main__':
	filename = 'finalized_model.sav'
	import pickle

	model = pickle.load(open(filename, 'rb'))

	token_filename = 'tokenizer.sav'
	tokenizer = pickle.load(open(token_filename, 'rb'))

	print(answer_question('when was my sprint planning?', text, tokenizer, model))