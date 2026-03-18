import math
import secrets
import string

from flask import Flask, g, render_template, request, Response, redirect, url_for
from flask_babel import Babel, gettext as _

app = Flask(__name__)
app.config["BABEL_DEFAULT_LOCALE"] = "en"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"

SUPPORTED_LANGS = ["pt", "en", "es"]


def get_locale():
    return getattr(g, "lang_code", "en")


babel = Babel(app, locale_selector=get_locale)

# fmt: off
_WORDS_PT = [
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

_WORDS_EN = [
    "anchor","anvil","apple","arrow","badge","basin","beach","blade",
    "blaze","bloom","board","brain","brave","brick","bridge","brook",
    "brush","cabin","camel","candy","cargo","cedar","chain","chalk",
    "charm","chase","chess","cliff","clock","cloud","cobra","coral",
    "crane","creek","crown","dance","delta","draft","dream","drift",
    "eagle","ember","fable","fence","flame","flask","flint","flood",
    "forge","frost","ghost","globe","glove","grain","grape","grove",
    "guard","guide","haven","hawk","heart","hedge","heron","honey",
    "ivory","jewel","joint","juice","knife","latch","layer","lemon",
    "light","linen","lodge","lunar","manor","maple","marsh","medal",
    "melon","metal","mirth","moose","mount","nexus","noble","north",
    "ocean","olive","orbit","otter","oxide","panel","patch","pearl",
    "pilot","plain","plank","plaza","plume","polar","pride","prism",
    "pulse","quail","quartz","quest","raven","ridge","river","robin",
    "royal","sable","scale","scout","shade","shark","shelf","shine",
    "shore","sigma","slate","slope","smoke","snake","solar","spade",
    "spark","spear","spine","spire","spray","stamp","steam","steel",
    "stone","storm","stove","sugar","surge","swift","sword","table",
    "talon","thorn","tiger","titan","torch","tower","trail","trout",
    "tulip","ultra","vault","vigor","vinyl","viper","vista","vivid",
    "wagon","waltz","watch","wheat","whale","width","witch","world",
    "yacht","zebra","aspen","bison","cider","denim","elfin","foyer",
    "glyph","hazel","inlet","jasper","knoll","lotus","mango","nylon",
    "oaken","pixel","radon","serif","topaz","umbra","woven","xylem",
]

_WORDS_ES = [
    "abeja","abismo","acero","adobe","aguja","aldea","aleta","alma",
    "ambar","ancla","angel","arbol","arena","arma","astro","atlas",
    "aurora","avion","azote","bahia","balsa","bambu","banco","barco",
    "barro","bello","bisne","bolsa","bosque","brasa","brisa","bruma",
    "buque","cable","calma","campo","canal","canto","carro","cauce",
    "cedro","cerco","choza","cielo","cinta","cisne","clave","clima",
    "cofre","coral","coyote","crema","crudo","cuero","cumbre","danza",
    "delta","diana","disco","doble","drago","duelo","dunas","eclipse",
    "elixir","enano","espada","fable","faro","ficha","finca","flauta",
    "flora","fonda","forja","fuego","gaita","garza","gemas","globo",
    "golpe","gordo","grano","gruta","guante","hacha","hielo","hierba",
    "huevo","idolo","impar","indio","istmo","jade","jaula","junco",
    "labio","lanza","largo","laurel","limon","lince","llama","llave",
    "lobo","loma","luna","magia","mango","manto","mapa","marca",
    "menta","metro","minas","monte","mural","nardo","nave","nicho",
    "noble","norte","nube","oasis","ocaso","oliva","opalo","orbe",
    "palma","panda","patio","perla","perno","piano","pinta","plata",
    "playa","poder","poema","polvo","postal","prado","pulpo","queso",
    "ramas","rastro","reina","reloj","risco","rocas","rosal","rumbo",
    "sable","sauce","selva","signo","sirena","solar","sonda","surco",
    "tabla","talon","tango","tigre","timbre","toldo","torre","trigo",
    "trono","trueno","tumba","tunel","turno","ultra","umbral","unico",
    "uranio","vaina","valle","vapor","veloz","venda","verde","vidrio",
    "viento","viola","visor","vivaz","volcan","zarpa","zebra","zorro",
]

_WORDS = {"pt": _WORDS_PT, "en": _WORDS_EN, "es": _WORDS_ES}
# fmt: on

_AMBIGUOUS = set("0Oo1lIi")
_WIFI_AMBIGUOUS = _AMBIGUOUS | set("S5B8Z2")


def _secure_sample(population: list, k: int) -> list:
    indices = set()
    while len(indices) < k:
        indices.add(secrets.randbelow(len(population)))
    return [population[i] for i in indices]


def generate_memorable(lang: str = "en") -> tuple[str, list[str]]:
    word_list = _WORDS.get(lang, _WORDS["en"])
    words = _secure_sample(word_list, 3)
    words = [w.capitalize() for w in words]
    sep = secrets.choice(["-", ".", "_"])
    number = str(secrets.randbelow(90) + 10)
    parts = [words[0], sep, words[1], sep, words[2], sep, number]
    return "".join(parts), parts


def generate_backup_code() -> str:
    digits = [secrets.choice(string.digits) for _ in range(8)]
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
        required.append(secrets.choice(upper))
    if use_lower and lower:
        charset += lower
        required.append(secrets.choice(lower))
    if use_numbers and digits:
        charset += digits
        required.append(secrets.choice(digits))
    if use_symbols and symbols:
        charset += symbols
        required.append(secrets.choice(symbols))

    if not charset:
        return ""

    remaining = max(0, length - len(required))
    chars = required + [secrets.choice(charset) for _ in range(remaining)]
    # Fisher-Yates shuffle with secrets
    for i in range(len(chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        chars[i], chars[j] = chars[j], chars[i]
    return "".join(chars)


def _format_crack_time(seconds: float) -> str:
    if seconds < 1:
        return _("instantâneo")
    if seconds < 60:
        return _("alguns segundos")
    if seconds < 3600:
        m = int(seconds / 60)
        return f"{m} {'minuto' if m == 1 else _('minutos')}"
    if seconds < 86400:
        h = int(seconds / 3600)
        return f"{h} {'hora' if h == 1 else _('horas')}"
    if seconds < 86400 * 365:
        d = int(seconds / 86400)
        return f"{d} {'dia' if d == 1 else _('dias')}"
    if seconds < 86400 * 365 * 1000:
        y = int(seconds / (86400 * 365))
        return f"{y} {'ano' if y == 1 else _('anos')}"
    if seconds < 86400 * 365 * 1_000_000:
        ky = int(seconds / (86400 * 365 * 1000))
        return _("%(n)s mil anos", n=ky)
    if seconds < 86400 * 365 * 1_000_000_000:
        my = int(seconds / (86400 * 365 * 1_000_000))
        return _("%(n)s milhões de anos", n=my)
    by = seconds / (86400 * 365 * 1_000_000_000)
    if by > 1000:
        return _("trilhões de anos")
    return _("%(n)s bilhões de anos", n=int(by))


def _crack_seconds(password: str) -> float:
    """Entropy-based crack time for cryptographically random passwords.

    Calculates the character pool from what's actually present, then
    estimates average time at 10 billion guesses/sec (GPU cluster,
    offline fast hashing like MD5/SHA-1 without salt).
    """
    pool = 0
    if any(c in string.ascii_lowercase for c in password):
        pool += 26
    if any(c in string.ascii_uppercase for c in password):
        pool += 26
    if any(c in string.digits for c in password):
        pool += 10
    if any(c in string.punctuation for c in password):
        pool += len(string.punctuation)  # 32
    if pool == 0:
        return 0
    entropy = len(password) * math.log2(pool)
    guesses_per_sec = 10_000_000_000
    return (2 ** entropy) / (2 * guesses_per_sec)


def password_strength(password: str) -> dict:
    seconds = _crack_seconds(password)

    # Score derived from crack time so label and time never contradict
    if seconds < 600:             # < 10 min
        score = 0
    elif seconds < 86400:         # < 1 day
        score = 1
    elif seconds < 86400 * 365:   # < 1 year
        score = 2
    elif seconds < 86400 * 365 * 1000:  # < 1000 years
        score = 3
    else:
        score = 4

    levels = {
        0: (_("Muito Fraca"), "text-red-500", "w-1/5", "bg-red-400"),
        1: (_("Fraca"), "text-orange-500", "w-2/5", "bg-orange-400"),
        2: (_("Moderada"), "text-yellow-600", "w-3/5", "bg-yellow-400"),
        3: (_("Forte"), "text-lime-600", "w-4/5", "bg-lime-500"),
        4: (_("Muito Forte"), "text-emerald-600", "w-full", "bg-emerald-500"),
    }
    row = levels[score]
    return {
        "label": row[0],
        "text_color": row[1],
        "bar_width": row[2],
        "bar_color": row[3],
        "crack_time": _format_crack_time(seconds),
    }


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


# ── Locale handling ──


@app.url_value_preprocessor
def pull_lang_code(endpoint, values):
    if values:
        g.lang_code = values.pop("lang_code", "en")
    else:
        g.lang_code = "en"


@app.context_processor
def inject_i18n():
    lang = getattr(g, "lang_code", "en")
    lang_labels = {"pt": "PT", "en": "EN", "es": "ES"}

    # Map endpoints to their localized URL patterns
    _url_map = {
        "index":   {"en": "/",            "pt": "/pt/",         "es": "/es/"},
        "privacy":     {"en": "/privacy",      "pt": "/pt/privacy",      "es": "/es/privacy"},
        "terms":       {"en": "/terms",        "pt": "/pt/terms",        "es": "/es/terms"},
        "methodology": {"en": "/methodology",  "pt": "/pt/methodology",  "es": "/es/methodology"},
    }

    def lang_url(code):
        endpoint = request.endpoint or "index"
        # For generate endpoint, map back to index
        if endpoint == "generate":
            endpoint = "index"
        return _url_map.get(endpoint, _url_map["index"]).get(code, "/")

    return {
        "lang_code": lang,
        "supported_langs": SUPPORTED_LANGS,
        "lang_labels": lang_labels,
        "lang_url": lang_url,
        "i18n_js": {
            "senha": _("senha"),
            "senhas": _("senhas"),
            "gerar": _("Gerar"),
            "gerar_senha": _("Gerar Senha"),
            "gerar_memoravel": _("Gerar Senha Memorizável"),
            "gerar_backup": _("Gerar Código de Backup"),
            "senhas_geradas": _("senhas geradas"),
            "sua_senha_gerada": _("Sua senha gerada"),
            "presets": {
                "personal":  {"label": _("Pessoal"),      "desc": _("uso diário")},
                "wifi":      {"label": _("Wi-Fi"),         "desc": _("redes domésticas")},
                "memorable": {"label": _("Memorizável"),   "desc": _("fácil de lembrar")},
                "pin":       {"label": _("PIN"),           "desc": _("desbloqueio")},
                "elderly":   {"label": _("Sênior"),        "desc": _("fácil de ler")},
                "backup":    {"label": _("Backup"),        "desc": _("recuperação")},
                "corporate": {"label": _("Corporativo"),   "desc": _("política de TI")},
                "master":    {"label": _("Master"),        "desc": _("cofre de senhas")},
                "legacy":    {"label": _("Legado"),        "desc": _("sistemas antigos")},
                "apikey":    {"label": _("API Key"),       "desc": _("integrações")},
                "token":     {"label": _("Token"),         "desc": _("acesso a APIs")},
                "shell":     {"label": _("Shell-safe"),    "desc": _("terminais bash")},
                "url":       {"label": _("URL-safe"),      "desc": _("configs e variáveis")},
            },
        },
    }


# ── Routes ──


@app.route("/")
@app.route("/<lang_code>/")
def index():
    if g.lang_code not in SUPPORTED_LANGS:
        return redirect("/")
    # Auto-detect language on root URL (no lang_code in path)
    if request.path == "/" and not request.args.get("hl"):
        best = request.accept_languages.best_match(SUPPORTED_LANGS, default="en")
        if best != "en":
            return redirect(f"/{best}/")
    return render_template("index.html")


@app.route("/privacy")
@app.route("/<lang_code>/privacy")
def privacy():
    if g.lang_code not in SUPPORTED_LANGS:
        return redirect("/privacy")
    return render_template(f"privacy_{g.lang_code}.html")


@app.route("/terms")
@app.route("/<lang_code>/terms")
def terms():
    if g.lang_code not in SUPPORTED_LANGS:
        return redirect("/terms")
    return render_template(f"terms_{g.lang_code}.html")


@app.route("/methodology")
@app.route("/<lang_code>/methodology")
def methodology():
    if g.lang_code not in SUPPORTED_LANGS:
        return redirect("/methodology")
    return render_template(f"methodology_{g.lang_code}.html")


@app.route("/robots.txt")
def robots():
    content = "User-agent: *\nAllow: /\nSitemap: https://oxepass.com/sitemap.xml\n"
    return Response(content, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://oxepass.com/</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://oxepass.com/" />
    <xhtml:link rel="alternate" hreflang="pt" href="https://oxepass.com/pt/" />
    <xhtml:link rel="alternate" hreflang="es" href="https://oxepass.com/es/" />
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://oxepass.com/privacy</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://oxepass.com/privacy" />
    <xhtml:link rel="alternate" hreflang="pt" href="https://oxepass.com/pt/privacy" />
    <xhtml:link rel="alternate" hreflang="es" href="https://oxepass.com/es/privacy" />
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
  <url>
    <loc>https://oxepass.com/terms</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://oxepass.com/terms" />
    <xhtml:link rel="alternate" hreflang="pt" href="https://oxepass.com/pt/terms" />
    <xhtml:link rel="alternate" hreflang="es" href="https://oxepass.com/es/terms" />
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
</urlset>"""
    return Response(content, mimetype="application/xml")


@app.route("/generate", methods=["POST"])
@app.route("/<lang_code>/generate", methods=["POST"])
def generate():
    pw_type = request.form.get("type", "random")
    count = max(1, min(10, int(request.form.get("count", 1))))
    exclude = request.form.get("exclude", "")

    entries = []

    for _ in range(count):
        if pw_type == "memorable":
            pwd, parts = generate_memorable(g.lang_code)
            entries.append({"password": pwd, "parts": parts})

        elif pw_type == "backup":
            pwd = generate_backup_code()
            entries.append({"password": pwd, "parts": None})

        elif pw_type == "shell":
            length = max(4, min(64, int(request.form.get("length", 20))))
            use_upper = request.form.get("uppercase") == "true"
            use_lower = request.form.get("lowercase") == "true"
            use_nums = request.form.get("numbers") == "true"
            shell_exclude = exclude + "!#$%^&*()[]{}|;<>?"
            pwd = generate_password(length, use_upper, use_lower, use_nums, True, exclude=shell_exclude)
            entries.append({"password": pwd, "parts": None})

        elif pw_type == "url":
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
