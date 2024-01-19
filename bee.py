from components import main

print('Bee [version: 1.0] released on [January 1, 2024]\nCreated by [Tahsin Ahmed] and copyright to [Cyberengine]\nFor more information, visit [www.bee-lang.com]\n')

while True:
    text = input('Bee > ')

    if text.strip() == "":
        continue

    result, error = main.run('<stdin>', text)

    if error:
        print(error.as_string())
    
    elif result:
        if len(result.elements) == 1:
            print(repr(result.elements[0]))
    
        else:
            print(repr(result))
