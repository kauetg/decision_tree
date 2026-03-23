# decision_tree 🌿

**A phenotypic similarity tool for field identification and education.**

Built by a biologist who codes, for biologists who need to identify things in the field — without a microscope, without a sequencer, without internet. Just what you can see.

---

## What it does

You define observable characters. You define your taxa. You fill the matrix.  
The app generates:

- 🌳 **A phenogram** — groups organisms by field-observable similarity
- 🔀 **A dichotomous key** — click YES or NO until you identify your organism
- 🔍 **A free search** — describe what you see, get ranked matches

The key and the phenogram are linked — as you navigate the key, the phenogram fades out the eliminated taxa in real time.

---

## What it is NOT

This is **not** a phylogenetic tool. Groups here reflect observable similarity, not evolutionary history. A snake and an earthworm could end up as sisters. A mosquito and a bird might cluster together.

Use this as a **field ID tool**, not a phylogeny. Your ecology professor will thank you.

---

## Built with

- **Python / Flask** — back-end core
- **scipy / numpy** — UPGMA clustering
- **ECharts** — interactive phenogram
- **Bootstrap 5** — clean, mobile-friendly UI

---

## Getting started

```bash
git clone https://github.com/kauetg/decision_tree
cd decision_tree
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000` and start building your matrix.

---

## Use cases

- 🪸 Coral reef field identification
- 🐟 Fish ID on scientific outings
- 🌿 Plant identification in forest surveys
- 🍞 Bread systematics (yes, really — it works beautifully)
- 📚 IB Biology — teaching character matrices and dichotomous keys

---

## Example datasets

Three ready-to-use datasets included in `/datasets`:

| Dataset | Taxa | Characters |
|---|---|---|
| Indo-Pacific hard corals | 8 | 5 |
| World breads | 8 | 5 |
| Italian pasta | 7 | 5 |

Load any of them from the `/test_data` folder via the **Load JSON** 
button on the main page.

---

## Roadmap

- [ ] Photo per character state (field visual reference)
- [ ] Offline mode / PWA for field use without internet
- [ ] Pre-defined character sets by taxonomic group
- [ ] MongoDB integration for persistent datasets
- [ ] Multi-language support

---

## A note on phenetics

This tool uses **phenetic clustering** (UPGMA) — grouping by overall similarity rather than shared evolutionary history. This was intentional. Observable characters in the field are what matter for identification, not molecular phylogenies.

The warning is built into the app. Teach it, discuss it, embrace it.

> *"A good field biologist knows what they're looking at.  
> A great field biologist knows why the tool works — and where it breaks."*

---

## License

MIT — use freely, modify openly, share generously.  
If this helps a student identify their first coral on a reef, it did its job.

---

## Contributing

Found a bug? Have a dataset to share? Open a PR or an issue.  
This tool was built for the field biology community — it should grow with it.

---

*Built with love in Bohol, Philippines by a passionate brazilian marine educator.*  
*Inspired by years of field work, good professors, and one very productive Sunday.*
