from PIL import Image
import os, argparse


w, h = 227, 227


def resizeMasked(img):
	global w, h
	if w == 0: s = 'w'
	elif h == 0: s = 'h'
	else: s = ''

	if len(s) > 0:
		if s == 'w':
			if h >= img.size[1]:
				w = img.size[0]
			else:
				fac = float(h) / img.size[1]
				w = int(img.size[0]*fac)
		else:
			if w >= img.size[0]:
				h = img.size[1]
			else:
				fac = float(w) / img.size[0]
				h = int(img.size[1]*fac)

	if img.size[0] == w and img.size[1] == h:
		return img

	if not (img.size[0] <= w and img.size[1] <= h):
		fac = float(w) / img.size[0]
		if int(img.size[1]*fac) > h: fac2 = float(h) / (img.size[1]*fac)
		else: fac2 = 1
		img = img.resize((int(round(img.size[0]*fac*fac2, 1)), int(round(img.size[1]*fac*fac2, 1))), Image.ANTIALIAS)

	black = Image.new(img.mode, (w, h), "black")
	if img.size[0] == w:
		black.paste(img, (0, int((h-img.size[1])/2.0)))
	else:
		black.paste(img, (int((w-img.size[0])/2.0), 0))
	
	return black


def resizeForced(img):
	global w, h
	if w == 0: s = 'w'
	elif h == 0: s = 'h'
	else: s = ''

	if len(s) > 0:
		if s == 'w': w = img.size[0]
		else: h = img.size[1]

	if img.size[0] == w and img.size[1] == h:
		return img

	return img.resize((w,h), Image.ANTIALIAS)


def resizeScaled(img):
	global w, h

	if w > 0 and h > 0:
		if img.size[0] == w and img.size[1] <= h:
			return img
		if img.size[0] <= w and img.size[1] == h:
			return img

		fac = float(w) / img.size[0]
		if int(img.size[1]*fac) > h: fac2 = float(h) / (img.size[1]*fac)
		else: fac2 = 1
		img = img.resize((int(round(img.size[0]*fac*fac2, 1)), int(round(img.size[1]*fac*fac2, 1))), Image.ANTIALIAS)
	elif w > 0:
		if img.size[0] == w: return img
		fac = float(w) / img.size[0]
		img = img.resize((w, int(img.size[1]*fac)), Image.ANTIALIAS)
	else:
		if img.size[1] == h: return img
		fac = float(h) / img.size[1]
		img = img.resize((int(img.size[0]*fac), h), Image.ANTIALIAS)

	return img


def transform(method, datasetDir, outputDir):
	for fn in os.listdir(datasetDir):
		try: img = Image.open(os.path.join(datasetDir, fn))
		except: continue

		img = method(img)

		img.save(os.path.join(outputDir, fn))
		print(fn)


if __name__ == "__main__":
	parser = argparse.ArgumentParser("Transform images. Methods: masked, scaled, forced (default) - to resize by 1D set irrelevant size to 0")
	parser.add_argument("imagesDir", type=str, help="path to images directory", nargs=1)
	parser.add_argument("outputDir", type=str, help="output directory (optional)", nargs='?')
	parser.add_argument("-m", action="store_true", help="masked - set irrelevant size to 0 to mask by 1D (image unresized)")
	parser.add_argument("-s", action="store_true", help="scaled - set irrelevant size to 0 (default: fitted and scaled within w x h)")

	parser.add_argument("--wh", help="set output size (default: {0}, {1})".format(str(w), str(h)), type=int, nargs=2)

	#parser.add_argument("--rr", help="rotate right (default: {0}, {1})".format(str(w), str(h)), type=int, nargs=1)
	#parser.add_argument("--rl", help="rotate left (default: {0}, {1})".format(str(w), str(h)), type=int, nargs=1) ne treba -90
	#parser.add_argument("--mirror u d", help="rotate right (default: {0}, {1})".format(str(w), str(h)), type=int, nargs=1)
	#parser.add_argument("--mirrorUpsideDown u d", help="rotate right (default: {0}, {1})".format(str(w), str(h)), type=int, nargs=1)

	args = parser.parse_args()

	datasetDir = os.path.abspath(args.imagesDir[0])
	if not os.path.exists(datasetDir):
		raise OSError(2, 'No such file or directory', datasetDir)

	if args.outputDir:
		outputDir = os.path.abspath(args.outputDir)
	else:
		outputDir = datasetDir + '_TransformImgsOUT'
	if not os.path.exists(outputDir): os.makedirs(outputDir)

	if args.wh: w, h = args.wh[0], args.wh[1]

	if w <= 0 and h <= 0:
		print("Wrong size: w = {0}, h = {1}".format(str(w), str(h)))
		raise SystemExit(0)

	if args.m:
		print("Method: masked")
		print("w = {0}, h = {1}".format(str(w), str(h)))
		method = resizeMasked
	elif args.s:
		print("Method: scaled")
		print("w = {0}, h = {1}".format(str(w), str(h)))
		method = resizeScaled
	else:
		print("Method: forced")
		print("w = {0}, h = {1}".format(str(w), str(h)))
		method = resizeForced
	
	transform(method, datasetDir, outputDir)
