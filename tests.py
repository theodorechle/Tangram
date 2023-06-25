def coucou(a):
    def inner(b, e):
        print(a, b, e)
        return a(b)
    return inner

@coucou
def salut(c):
    print(c)
    return c

print(salut(5, 7))