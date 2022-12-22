import requests

x = 3.333334950
y = 2.889329749
z = 9.2134899729
URL = ("https://maker.ifttt.com/trigger/fall_detected/with/key/bZ5RcrGNtpyWza0jDm1KzZ?value1={a}&value2={b}&value3={c}").format(
    a = x,
    b = y,
    c = z
)
requests.get(url = URL)