import random
import string

from flask import Flask, render_template, request, Response

app = Flask(__name__)

# fmt: off
_WORDS = [
    "abacaxi","abismo","agulha","alcova","aldeia","amanho","ancora","anjo",
    "aranha","areia","aroma","arvore","asas","astro","atlas","aurora",
    "aviao","azul","bairro","baleia","bambu","banana","barco","basalto",
    "beija","bigode","bolsa","bosque","braco","brisa","buraco","buzina",
    "cabra","cacau","calma","camelo","campo","canto","caoba","carro",
    "casca","cavalo","chuva","cidade","cinza","cobra","colmeia","coral",
    "corvo","couve","cozinha","cravo","cristal","dagua","danca","deserto",
    "diabo","diamante","dobra","dragao","dunas","eclipse","egua","elmo",
    "enxame","escudo","espada","estrela","faca","farinha","ferro","festa",
    "figueira","flecha","floresta","folha","fonte","forja","fosse","fruta",
    "fumo","furacao","gaiola","gato","gaviao","geada","glaciar","globo",
    "golfinho","graxa","gruta","guarana","guarda","ilhota","inverno","jardim",
    "joelho","junco","lancha","lapis","laranja","leao","lentilha","lima",
    "lince","lobo","lombo","lua","luva","macaco","magia","manto",
    "maraca","marinho","mato","melodia","mestre","milho","mirtilo","monte",
    "navio","nebula","nevoeiro","ninho","norte","nuvem","oceano","oliva",
    "onca","orgulho","orvalho","ostra","ourico","painel","palma","panela",
    "pantano","papiro","passaro","patins","pedra","peixe","pena","petala",
    "piloto","pinheiro","pipa","planeta","polvos","pombo","portal","pouso",
    "prata","preto","primo","pulga","radar","raio","raposa","raiz",
    "reino","relva","remo","riacho","risca","robalo","rocha","rolha",
    "roxo","ruivo","sabao","sabre","safira","sapo","selva","semente",
    "serra","signo","sino","sistema","soalho","sobra","solar","sonho",
    "sorte","suco","tabua","talco","tarefa","templo","tigre","tinta",
    "toalha","tornado","totem","trovao","tucano","tulipa","tundra","turvo",
    "ubere","ultra","umbra","unico","urano","urso","uva","vaca",
    "valsa","vapor","vela","veneno","vento","verde","vidro","viola",
    "virado","visor","vista","vitoria","voador","vulcao","xadrez","zebra",
]
# fmt: on

# Chars that look alike — removed in "child" and "wifi" modes
_AMBIGUOUS = set("0Oo1lIi")
# Extended set for Wi-Fi: also removes digits/letters easily confused across cases
_WIFI_AMBIGUOUS = _AMBIGUOUS | set("S5B8Z2")


def generate_memorable() -> tuple[str, list[str]]:
    words = random.sample(_WORDS, 3)
    words = [w.capitalize() for w in words]
    sep = random.choice(["-", ".", "_"])
    number = str(random.randint(10, 99))
    parts = [words[0], sep, words[1], sep, words[2], sep, number]
    return "".join(parts), parts


def generate_backup_code() -> str:
    """8-digit code split into two groups of 4, e.g. '3821 9047'."""
    digits = [random.choice(string.digits) for _ in range(8)]
    return f"{''.join(digits[:4])} {''.join(digits[4:])}"


def generate_password(
    length: int,
    use_upper: bool,
    use_lower: bool,
    use_numbers: bool,
    use_symbols: bool,
    exclude: str = "",
    child_mode: bool = False,
    wifi_mode: bool = False,
) -> str:
    symbols_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    charset = ""
    required = []

    if child_mode:
        ambiguous = _AMBIGUOUS
    elif wifi_mode:
        ambiguous = _WIFI_AMBIGUOUS
    else:
        ambiguous = set()
    blocked = set(exclude) | ambiguous

    def clean(s: str) -> str:
        return "".join(c for c in s if c not in blocked)

    upper = clean(string.ascii_uppercase)
    lower = clean(string.ascii_lowercase)
    digits = clean(string.digits)
    symbols = clean(symbols_chars)

    if use_upper and upper:
        charset += upper
        required.append(random.choice(upper))
    if use_lower and lower:
        charset += lower
        required.append(random.choice(lower))
    if use_numbers and digits:
        charset += digits
        required.append(random.choice(digits))
    if use_symbols and symbols:
        charset += symbols
        required.append(random.choice(symbols))

    if not charset:
        return ""

    remaining = max(0, length - len(required))
    chars = required + [random.choice(charset) for _ in range(remaining)]
    random.shuffle(chars)
    return "".join(chars)


def password_strength(password: str) -> dict:
    score = 0
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1
    if len(password) >= 16:
        score += 1

    levels = {
        1: ("Muito Fraca", "text-red-500", "w-1/5", "bg-red-400"),
        2: ("Fraca", "text-orange-500", "w-2/5", "bg-orange-400"),
        3: ("Moderada", "text-yellow-600", "w-3/5", "bg-yellow-400"),
        4: ("Forte", "text-lime-600", "w-4/5", "bg-lime-500"),
        5: ("Muito Forte", "text-emerald-600", "w-full", "bg-emerald-500"),
    }
    default = ("Muito Fraca", "text-red-500", "w-1/5", "bg-red-400")
    row = levels.get(score, default)
    return {"label": row[0], "text_color": row[1], "bar_width": row[2], "bar_color": row[3]}


@app.template_filter("select_upper")
def select_upper(s):
    return any(c.isupper() for c in s)


@app.template_filter("select_lower")
def select_lower(s):
    return any(c.islower() for c in s)


@app.template_filter("select_digit")
def select_digit(s):
    return any(c.isdigit() for c in s)


@app.template_filter("select_symbol")
def select_symbol(s):
    return any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in s)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/privacidade")
def privacy():
    return render_template("privacy.html")


@app.route("/termos")
def terms():
    return render_template("terms.html")


@app.route("/robots.txt")
def robots():
    content = "User-agent: *\nAllow: /\nSitemap: https://oxepass.com/sitemap.xml\n"
    return Response(content, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://oxepass.com/</loc>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://oxepass.com/privacidade</loc>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
  <url>
    <loc>https://oxepass.com/termos</loc>
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
</urlset>"""
    return Response(content, mimetype="application/xml")


@app.route("/generate", methods=["POST"])
def generate():
    pw_type = request.form.get("type", "random")
    count = max(1, min(10, int(request.form.get("count", 1))))
    exclude = request.form.get("exclude", "")

    entries = []  # list of {"password": str, "parts": list|None}

    for _ in range(count):
        if pw_type == "memorable":
            pwd, parts = generate_memorable()
            entries.append({"password": pwd, "parts": parts})

        elif pw_type == "backup":
            pwd = generate_backup_code()
            entries.append({"password": pwd, "parts": None})

        elif pw_type == "shell":
            # Shell-safe: symbols without bash metacharacters; keeps @ _ + - = : , .
            length = max(4, min(64, int(request.form.get("length", 20))))
            use_upper = request.form.get("uppercase") == "true"
            use_lower = request.form.get("lowercase") == "true"
            use_nums = request.form.get("numbers") == "true"
            shell_exclude = exclude + "!#$%^&*()[]{}|;<>?"
            pwd = generate_password(length, use_upper, use_lower, use_nums, True, exclude=shell_exclude)
            entries.append({"password": pwd, "parts": None})

        elif pw_type == "url":
            # URL-safe: symbols limited to - _ . (RFC 3986 unreserved)
            length = max(4, min(64, int(request.form.get("length", 20))))
            use_upper = request.form.get("uppercase") == "true"
            use_lower = request.form.get("lowercase") == "true"
            use_nums = request.form.get("numbers") == "true"
            url_exclude = exclude + "!@#$%^&*()+=[]{}|;:,<>?"
            pwd = generate_password(length, use_upper, use_lower, use_nums, True, exclude=url_exclude)
            entries.append({"password": pwd, "parts": None})

        else:
            length = max(4, min(64, int(request.form.get("length", 16))))
            use_upper = request.form.get("uppercase") == "true"
            use_lower = request.form.get("lowercase") == "true"
            use_nums = request.form.get("numbers") == "true"
            use_syms = request.form.get("symbols") == "true"
            child   = pw_type == "child"
            elderly = pw_type == "elderly"
            wifi    = pw_type == "wifi"

            if not any([use_upper, use_lower, use_nums, use_syms]):
                use_lower = True

            pwd = generate_password(length, use_upper, use_lower, use_nums, use_syms, exclude=exclude, child_mode=child or elderly, wifi_mode=wifi)
            entries.append({"password": pwd, "parts": None})

    strength = password_strength(entries[0]["password"])

    return render_template(
        "partials/password_result.html",
        entries=entries,
        strength=strength,
        pw_type=pw_type,
    )


if __name__ == "__main__":
    app.run(debug=True, port=8080, ssl_context="adhoc")
