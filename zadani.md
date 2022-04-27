# Vyhledání a extrakce kryptoměnových adres v nestrukturovaných zdrojích (Daniel Dolejška)

## Zadání

K dispozici dostanete dataset obsahující archiv stažených webových stránek historicky aktivních temných tržišť (darknet marketplace) a některých darknetových diskuzních fór. Tyto webové stránky mohou obsahovat různé zajímavé informace.

Vašim cílem bude implementace nástroje pro efektivní vyhledávání a extrakci adres kryptoměnových peněženek, které se v daných datech mohou nacházet. Součástí extrakce musí být i "tagování" nalezených adres (v jakém kontextu byly nalezeny - název portálu, uživatelské jméno, ...) K implementaci můžete využít libovolný programovací jazyk a jakékoliv relevantní nástroje a knihovny třetích stran. Součástí řešení projektu bude i dokumentace, kde bude popsáno:
- použité knihovny a nástroje,
- zvolené či navržené korelační metody,
- implementace výsledného nástroje,
- dosažené výsledky - benchmark, počty nalezených adres, jejich typy atd.

V rámci tohoto projektu bude žádoucí určitá úroveň týmové kooperace, protože poskytnutá datová sada není úplně malá (uncompressed ~1.5TB).

V případě nejasností či dalších otázek k zadání kontaktujte zadávajícího projektu.

### Shrnutí

Hlavními cíli tohoto projektu je tedy:
1. implementace nástroje pro extrakci a tagování adres kryptoměnových peněženek z poskytnutého zdrojového datasetu,
2. vytvoření výstupního datasetu obsahující nalezené a otagované adresy,
3. zhodnocení dosažených výsledků.

## Email 1

Na https://www.gwern.net/DNM-archives najdete dataset se kterým budete při řešení tohoto projektu pracovat. Dataset si mezi sebou klidně budete moci nějak poměrově rozdělit.

Společnou úvodní konzultaci si můžeme domluvit prostřednictvím https://doodle.com/poll/uf5sk5z9tbemifec. Zde se domluvíme co od Vás v rámci daného projektu očekávám.

## Email 2

Vzhledem k tomu, že by se na úvodní konzultaci nesešla ani půlka ze zapsaných napíšu jen stručně informace k projektu:

Cílem je nalezení jakýchkoliv kryptoměnových adres (BTC, ETH, LTC, …) a jejich otagování užitečnými informacemi:
- na jakém webu, či přesněji stránce, byly nalezeny,
- pokud se vztahují ke konkrétnímu uživateli, tak k jakému,
- pokud patří tržišti/či jiné webové službě, pak jaké,
- do jaké kategorie daná adresa spadá (gambling, darkmarket, směnárna atd.),
- jakékoliv další užitečné informace.

Další poznámky k řešení projektu:
- celý dataset si mezi sebou poměrově rozdělte - obsahy stránek jsou heterogenní,
- výstupní formát bude unifikovaný a pro všechny stejný - ten Vám zadám v průběhu semestru,
- jazyk implementace a použité knihovny jsou bez omezení (rychlost bude důležitá - dataset je velký),
- na téma konečného obsahu dokumentace se ještě pobavíme později.

Pokud máte nejasnosti či otázky a chtěli byste na úvodní konzultaci dorazil, tak mi napište mail a domluvíme se na termínu separátně. Můžeme se sejít tady na fakultě či si jen zavolat přes Discord, Teamsy, Jitsi nebo cokoliv jiného.
