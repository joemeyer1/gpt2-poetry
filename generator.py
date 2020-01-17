
import json
import os
import sys
import numpy as np
import tensorflow as tf

from src import model, sample, encoder


class Generator:

	def __init__(self,
				model_name='117M',
				seed=None,
				batch_size=6,
				length=1,
				temperature=1,
				top_k=0,
				top_p=0.0,
				ckpt = 'checkpoint/12-8'
	):
		"""
		:model_name=117M : String, which model to use
		:seed=None : Integer seed for random number generators, fix seed to reproduce
		 results
		:batch_size=1 : Number of batches (only affects speed/memory).
		:length=None : Number of tokens in generated text, if None (default), is
		 determined by model hyperparameters
		:temperature=1 : Float value controlling randomness in boltzmann
		 distribution. Lower temperature results in less random completions. As the
		 temperature approaches zero, the model will become deterministic and
		 repetitive. Higher temperature results in more random completions.
		:top_k=0 : Integer value controlling diversity. 1 means only 1 word is
		 considered for each step (token), resulting in deterministic completions,
		 while 40 means 40 words are considered at each step. 0 (default) is a
		 special setting meaning no restrictions. 40 generally is a good value.
		:top_p=0.0 : Float value controlling diversity. Implements nucleus sampling,
		 overriding top_k if set to a value > 0. A good setting is 0.9.
		"""

		self.seed = seed
		self.batch_size = batch_size		
		self.enc = encoder.get_encoder(model_name)
		self.hparams = model.default_hparams()
		self.temperature=temperature
		self.top_k = top_k
		self.top_p = top_p
		self.model_name = model_name
		self.length = length
		self.endoftext = self.enc.encode('<|endoftext|>')

		if ckpt:
			self.ckpt = ckpt
		else:
			self.ckpt = os.path.join('models', self.model_name)

		with open(os.path.join('models', model_name, 'hparams.json')) as f:
			self.hparams.override_from_dict(json.load(f))
		if length is None:
			length = self.hparams.n_ctx // 2
		elif length > self.hparams.n_ctx:
			raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)


	def generate(self, prompt=''):
		with tf.Session(graph=tf.Graph()) as sess:

			np.random.seed(self.seed)
			tf.set_random_seed(self.seed)

			# enc.encoder['<|endoftext|>'] is different and does worse
			prompt = '<|endoftext|>'+prompt

			# if not prompt:
			# 	start_token = self.enc.encoder['<|endoftext|>']
			
			
			context = tf.placeholder(tf.int32, [self.batch_size, None])

			output = sample.sample_sequence(
				hparams=self.hparams, length=self.length,
				context=context,
				batch_size=self.batch_size,
				temperature=self.temperature, top_k=self.top_k, top_p=self.top_p
			)

			saver = tf.train.Saver()
			ckpt = tf.train.latest_checkpoint(self.ckpt)
			saver.restore(sess, ckpt)	

			context_tokens = self.enc.encode(prompt)
			while True:
				# save old text to show in decision
				pre_token_text = self.enc.decode(context_tokens[len(self.endoftext):]) 
				# generate token batch
				#	context_tokens.copy() to avoid modifying context_tokens
				new_tokens = self.get_output(output, sess, context, context_tokens.copy())
				# iterate through batch until token selected or all of batch shown
				for new_token in new_tokens:
					# decode token
					new_text = self.enc.decode(new_token)
					# decide token
					new_text, reset_prompt = self.decide(new_text, pre_token_text)
					if reset_prompt:
						context_tokens = self.enc.encode(prompt)
						break
					# backtrack if required
					elif type(new_text) == int and new_text > 0:
						new_text = min(new_text, len(context_tokens)-len(self.endoftext))
						context_tokens = context_tokens[:-new_text]
						break
					# update context
					elif new_text:
						context_tokens += self.enc.encode(new_text)
						break

				

			return text



	def get_output(self, output, sess, context, context_tokens):
		# get tokens
		if context != None:
			# conditional generation
			tokens, logits = sess.run(output, feed_dict={
				context: [context_tokens for _ in range(self.batch_size)]
			})
			# extract newly generated token (discard context)
			tokens = tokens[:, len(context_tokens):]
		else:
			# unconditional generation
			# get generated token (there is no context to discard here)
			tokens, logits = sess.run(output)

		return tokens

	def decide(self, new_text, old_text):
		# '\x7f':del, '\x1b':arrowkey, '\r':enter, '\\': del chunk and 's':save
		#		interrupt = \x03:ctr-c or \x1a:ctrl-z or 'q'

		reset_prompt = False
		# loop until decision received
		decision_received = False
		while not decision_received:
			# assume user inputs correctly, correct if they don't
			decision_received = True
			os.system('clear')
			print('\033[A\033[2K')
			print("{}::{}".format(old_text, new_text), end='', flush=True)
			# get user feedback
			char = getch()
			if char == '\x7f': # reject token
				new_text = ''
			elif char == '\x1b': # custom text
				new_text = self.get_custom_text(old_text)
			elif char == '\\': # delete chunk
				new_text = self.delete_chunk(old_text)
			elif char == 's':
				self.save_poem(old_text)
				new_text = ''
			elif char == 'r':
				new_text = ''
				reset_prompt = True
			elif char in ('\x03', '\x1a', 'q'):
				raise Exception("Exiting Upon User Request...")
			elif char != '\r':
				decision_received = False
				print("\n\npress 'enter' to accept")
				print("press 'delete' to reject")
				print("press an arrowkey to edit")
				print("press backslash to delete chunk")
				print("press 's' to save")
				print("press 'r' to reset prompt")
				print("press 'q' to quit\n")
				print("(press any key to acknowledge these instructions.)\n", flush=True)
				# wait for user acknowledgement of instructions
				_ = getch()
				# try again (we're in a while loop)

		return new_text, reset_prompt

	# helper for self.decide()
	def delete_chunk(self, old_text):
		os.system('clear')
		print('\033[A\033[2K')
		text_tokens = [self.enc.decode([token]) for token in self.enc.encode(old_text)]
		n_tokens = len(text_tokens)
		for t in range(n_tokens):
			token = text_tokens[t]
			print(str(n_tokens-t-1)+'::'+token)
		print('\n\n'+'='*15)
		new_text = False
		while type(new_text) != int:
			try:
				new_text = min(int(input()), len(text_tokens))
			except:
				print("# Tokens To Remove: ")
		# # process the enter key
		# _ = getch()
		# _ = getch()
		return new_text

	# helper for self.decide()
	def get_custom_text(self, old_text):
		# get custom text
		custom_text = self.write_text_get_input(old_text)
		# # process the enter key
		# _ = getch()
		# _ = getch()
		# If user immediately pressed 'enter' then that's their input
		if not custom_text:
			custom_text = '\n'

		return custom_text

	# write poem to file (ask user for filename)
	def save_poem(self, poem):
		filename = ''
		prompt = ''
		while not filename:
			prompt += "\nEnter File Name::"
			filename = self.write_text_get_input(poem, prompt)
			filename, prompt = self.is_valid(filename)
		with open(filename, 'w') as f:
			f.write(poem)
		return ''

	# helper for Generator.save_poem(); returns filename if valid - else empty string
	def is_valid(self, filename):
		split_filename = filename.split('.')
		# check if input is invalid
		#	i.e. if it has extra '.'s or is empty or not alphanumeric
		valid_name = True
		if len(split_filename) > 2 or not split_filename[0]:
			valid_name = False
		else:
			for character in split_filename[0]:
				if not character.isalnum() and character not in ('-', '_'):
					valid_name = False
					break
		if not valid_name:
			prompt = "\n{} is not a valid filename.".format(filename)
			filename = ''
		else:
			# if user excluded file extension, add it
			if len(split_filename) == 1:
				prompt = ''
				filename = filename+'.txt'
			# if file already exists don't overwrite
			if os.path.isfile(filename):
				prompt = "\n{} already exists. Please enter a different filename.".format(filename)
				filename = ''

		return filename, prompt


	def write_text_get_input(self, text, input_prompt=''):
		os.system('clear')
		print('\033[A\033[2K', flush=True)
		print("{}::".format(text), end='', flush=True)
		user_input = input(input_prompt)
		return user_input



import sys, termios, tty, os, time
# capture arrow key stroke 
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
 
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch



