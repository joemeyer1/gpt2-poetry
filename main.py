

from generator import Generator
import fire

def main(checkpoint_dir="checkpoint/12-8", prompt=''):
	global g;
	g = Generator(ckpt=checkpoint_dir)
	# fire does weird stuff to linebreaks; undo it
	prompt = prompt.replace('\\n', '\n')
	g.generate(prompt=prompt)


fire.Fire(main)