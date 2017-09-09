def getContactInfo(doc):

# filename = "previous_data/1-100/Food_article_20170909.json"

	ADDR_PATTERNS= [
		"地址 ",
		"地址:",
		"地址：",
		"地點 ",
		"地點:",
		"地點：",
	]

	TEL_PATTERNS= [
		"電話 ",
		"電話:",
		"電話：",
		"ＴＥＬ ",
		"ＴＥＬ:",
		"ＴＥＬ：",
		"TEL ",
		"TEL:",
		"TEL：",
	]


	lines = doc.split("\n")
	address = ''
	phone = ''
	isNext = False
	for line in lines:
		line = line.strip()
		for pat in ADDR_PATTERNS:
			if line.find(pat)!=-1:
				addr = line[line.find(pat)+3:]
				if len(addr)==0:
					isNext = True
					break
				# print("{} {}".format(pat, addr))
				address = addr
				break
	
	for line in lines:
		line = line.strip()
				#if isNext:
				#	art["tel"].append(line) 
				#	print("next: {}".format(line))
				#	isNext = False
				#	break
		for pat in TEL_PATTERNS:
			if line.find(pat)!=-1:
				addr = line[line.find(pat)+3:]
				if len(addr)==0:
					isNext = True
					break
				# print("{} {}".format(pat, addr))
				phone = addr
				break

	return address, phone