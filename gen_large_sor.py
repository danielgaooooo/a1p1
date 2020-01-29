with open('large.sor', 'w') as f:
    line = '<0>  <asdf  ><12.0 >< +124>\n'
    for i in range(100000):
        f.write(line)
    line = '<1>  <ghjkl  ><13.0 >< -125>\n'
    for i in range(100000):
        f.write(line)
    line = '<1>  <tyui  ><+0.2 >< -130>\n'
    for i in range(100000):
        f.write(line)
    line = '<1>  <tyui  ><+0.2 >< -131>\n'
    f.write(line)