import json

#Update this
DISCOURSE_API_KEY = 'YOUR_API_TOKEN'

#Function for determining if a post has a body or not
def hasBody(row):
    if 'body' in row['content_json'].keys() and row['content_json']['body'] != "":
        return True
    else:
        return False

#Function to extract text from content_json
def extractText(content_json):
    try:
        return json.loads(content_json['body'])['blocks']
    except:
        #Sometimes the body is just a regular old string
        return content_json['body']

#Function to extract title from content_json
def extractTitle(row):
    return row['content_json']['title']

#####################
## Markdown parser ##
#####################
def formatText(content_json):

    #Initialize list number variable for ordered lists
    last_list_number = 1
    #Initialize variable to store previous item type
    prev_type = ''
    text = ''

    #Extract text
    text_block = extractText(content_json)

    #Iterate through each block of text
    for item in text_block:

        #If there's no content, skip
        if len(item) == 1:
            continue

        #If it's an ordered list item, prepend with the current last_list_number
        if item['type'] == 'ordered-list-item':
            line = str(last_list_number) + '. ' + item['text']
            last_list_number += 1

        else:
            #If unordered list item, put a dash before it
            if item['type'] == 'unordered-list-item':
                line = '- ' + item['text']

            #If header one text, put a # before it
            elif item['type'] == 'header-one':
                line = '# ' + item['text']

            #If header two text, put a ## before it
            elif item['type'] == 'header-two':
                line = '## ' + item['text']

            #If header three text, put a ## before it
            elif item['type'] == 'header-three':
                line = '### ' + item['text']

            #If unstyled, just pass through text
            else:
                line = item['text']

            #If we've just finished a list, reset the last_list_number counter
            if prev_type == 'ordered-list-item':
                last_list_number = 1

            #Update line based on inline styles
            if item['inlineStyleRanges'] != []:
                #Iterate through each inline style
                for style in item['inlineStyleRanges']:
                    #Extract the offset and add offset for every markdown character we add
                    offset = style['offset'] + line.count('`') + line.count('**') + line.count('#')
                    #Extract length
                    length = style['length']
                    #The offset doesn't include the dashes we're adding to format markdown bullets
                    if line[0:2] == "- ":
                        offset += 2 
                    #If the inline style is code, add markdown formatting
                    if style['style'] == 'CODE':
                        line = line[:offset] + "`" + line[offset:offset+length] + "`" + line[offset+length:]
                    #If the inline style is bold, add bold formatting
                    if style['style'] == 'BOLD':
                        line = line[:offset] + "**" + line[offset:offset+length] + "**" + line[offset+length:]
                    #Should probably add italics in here at some point...

            #If the text item has an associated image or hyperlink, get the key and grab the url from entityMap
            if item['entityRanges'] != []:
                #Extract the entity's key 
                entity_key = item['entityRanges'][0]['key']
                #Extract the entityMap data
                data = json.loads(content_json['body'])['entityMap'][str(entity_key)]
                #If the entity is an image
                if data['type'] == 'IMAGE':
                    #Get the url for the hosted image
                    url = data['data']['src']
                    try:
                        #If the image has an alt, add markdown formatting for image with alt
                        alt = data['data']['alt']
                        line += "<br/>![{}]({})".format(alt, url) + "<br/>"
                    #If the image doesn't have an alt, add markdown formatting for image without alt
                    except: 
                        line += "<br/>![]({})<br/>".format(url)
                #If the entity is a hyperlink
                elif data['type'] == 'LINK':
                    #Get the hyperlink URL
                    url = data['data']['url']
                    #Extract the offset and add offset for every markdown character we add
                    offset = item['entityRanges'][0]['offset'] + line.count('`') + line.count('**') + line.count('#')
                    #Extract length
                    length = item['entityRanges'][0]['length']
                    #The offset doesn't include the dashes we're adding to format markdown bullets
                    if line[0:2] == "- ":
                        offset += 2
                    #Add markdown formatting for hyperlink
                    line = line[:offset] + "[" + line[offset:offset+length] + "]({})".format(url) + line[offset+length:]

        #Add the current line to the text variable
        text += line
        #Add a line break
        text += ' \n'
        #Set the previous item type
        prev_type = item['type']
    
    return text