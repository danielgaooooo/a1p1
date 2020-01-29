with open('large.sor', 'w') as f:
    line = '<0>  <asdf  ><12.0 >< +124>\n'
    for i in range(99999):
        f.write(line)