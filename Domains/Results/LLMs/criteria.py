CRITERIA_BY_PAGE_TYPE = {
    "global": {
        "navigation_findability": {
            "title": "Navigation & Findability",
            "summary": (
                "Assesses how quickly a new shopper can grasp site structure, move between "
                "key pages (home ⇄ category ⇄ product ⇄ cart), and locate a specific item. "
                "Relies on obvious labels, visible search, sensible hierarchy, orientation cues "
                "(breadcrumbs), and clear recovery paths to cut friction and boost conversion."
            ),
            "scoring_criteria": [
                {
                    "name": "Menu clarity & placement",
                    "what_to_look_for": "Global nav visible on every page with plain‑language category names.",
                    "how_to_judge": "Hidden or cryptic labels lower score; obvious, self‑evident labels raise."
                },
                {
                    "name": "Hierarchy & grouping",
                    "what_to_look_for": "Logical grouping, mega‑menu or sub‑menus sized to catalog.",
                    "how_to_judge": "Mis‑grouped or overly deep nesting penalizes."
                },
                {
                    "name": "Search bar visibility",
                    "what_to_look_for": "Search field above the fold on all pages with hint text ('Search products…').",
                    "how_to_judge": "Hard‑to‑spot, missing, or home‑only search lowers."
                },
                {
                    "name": "Search assistance",
                    "what_to_look_for": "Autocomplete, spell‑check, suggestions speeding queries.",
                    "how_to_judge": "No assistive features deduct up to one point."
                },
                {
                    "name": "Orientation cues",
                    "what_to_look_for": "Breadcrumbs or highlighted current section.",
                    "how_to_judge": "Absent cues lower confidence and score."
                },
                {
                    "name": "Error‑recovery paths",
                    "what_to_look_for": "Logo‑to‑home link, 'Back to results,' persistent cart link.",
                    "how_to_judge": "Dead‑ends or orphan pages cost points."
                }
            ],
            "scoring_guide": {
                1: {
                    "label": "Very Poor",
                    "quick_diagnostic": "User lost; menu absent/mislabeled; no search or buried search.",
                    "example": "URL '/products?id=123' shows no menu, no route back."
                },
                2: {
                    "label": "Poor",
                    "quick_diagnostic": "Menu exists but vague ('Stuff', 'More'); minuscule footer search.",
                    "example": "Click 'Accessories' expecting phone cases, land on unrelated gadgets."
                },
                3: {
                    "label": "Average",
                    "quick_diagnostic": "Basic nav works; some labels off; breadcrumbs sporadic.",
                    "example": "'Electronics > Phones' path clear, but search only in desktop header."
                },
                4: {
                    "label": "Good",
                    "quick_diagnostic": "Clear categories, prominent search, consistent breadcrumbs; minor tweaks left.",
                    "example": "Mega‑menu lists 'Laptops', 'Tablets', 'Phones'; auto‑suggest shows top hits."
                },
                5: {
                    "label": "Excellent",
                    "quick_diagnostic": "Instant catalog comprehension; well‑organized menus; smart search; flawless breadcrumbs.",
                    "example": "Apple.com‑like layout – omnipresent search, intuitive categories, no dead‑ends."
                }
            }
        },
        "visual_design_aesthetics": {
            "title": "Visual Design & Aesthetics",
            "summary": (
                "How visually appealing, modern, and trustworthy the page looks at first glance. "
                "Focus on layout balance, use of whitespace, harmonious color palette, clear typography, "
                "high‑quality imagery, and overall consistency. Good design should draw attention to key elements "
                "(product photos, CTAs) while maintaining brand cohesion and readability."
            ),
            "scoring_criteria": [
                {
                    "name": "Layout & whitespace",
                    "what_to_look_for": "Balanced grid or modular layout with sufficient breathing space around elements.",
                    "how_to_judge": "Crowded, misaligned, or inconsistent spacing lowers the score; generous, well‑structured spacing raises it."
                },
                {
                    "name": "Typography clarity & size",
                    "what_to_look_for": "Legible font choices, appropriate hierarchy of headings, body, and captions.",
                    "how_to_judge": "Tiny fonts, odd typefaces, or inconsistent heading styles reduce the score; clear, consistent type raises it."
                },
                {
                    "name": "Color scheme & contrast",
                    "what_to_look_for": "Brand‑aligned palette, adequate contrast for readability, and restrained use of accent colors.",
                    "how_to_judge": "Clashing hues or poor contrast deduct points; harmonious palette with purposeful highlights adds points."
                },
                {
                    "name": "Imagery quality & relevance",
                    "what_to_look_for": "High‑resolution product photos or lifestyle images that match the brand mood.",
                    "how_to_judge": "Pixelated, stretched, or generic stock images penalize; crisp, well‑lit, on‑brand visuals reward."
                },
                {
                    "name": "Visual hierarchy & emphasis",
                    "what_to_look_for": "Clear focal points guiding the eye (F‑ or Z‑pattern), CTAs in contrasting colors.",
                    "how_to_judge": "Important elements lost in clutter or low contrast lower the score; obvious, intuitive emphasis raises it."
                },
                {
                    "name": "Styling consistency across pages",
                    "what_to_look_for": "Same fonts, colors, button shapes, and icon styles throughout the site.",
                    "how_to_judge": "Random changes in style or outdated elements reduce trust and score; seamless consistency boosts it."
                }
            ],
            "scoring_guide": {
                1: {
                    "label": "Very Poor",
                    "quick_diagnostic": "Outdated look, clashing colors, unreadable text, low‑quality images; feels spammy or unsafe.",
                    "example": "Neon green text on dark red background, clip‑art graphics, and five different fonts in one view."
                },
                2: {
                    "label": "Poor",
                    "quick_diagnostic": "Basic structure exists but cluttered with ads/pop‑ups; inconsistent fonts or misaligned sections.",
                    "example": "Homepage with three competing banners, two pop‑ups, and headings in different font families."
                },
                3: {
                    "label": "Average",
                    "quick_diagnostic": "Clean enough and consistent, yet unremarkable; minor clutter or weak CTA emphasis.",
                    "example": "Acceptable grid and color scheme, but CTA button blends with other elements and whitespace feels tight."
                },
                4: {
                    "label": "Good",
                    "quick_diagnostic": "Modern, well‑organized design; strong product imagery; clear CTA contrast; minor tweaks left.",
                    "example": "Plenty of whitespace, uniform font stack, large product photos; could use slightly bolder CTA style."
                },
                5: {
                    "label": "Excellent",
                    "quick_diagnostic": "Polished, professional aesthetic that inspires trust instantly; perfect hierarchy and cohesive branding.",
                    "example": "High‑end fashion site with elegant typography, hi‑res editorial imagery, and a standout “Add to Cart” button."
                }
            }
        }

    },
    "landing": {
        "visual_hierarchy_focus": {
            "title": "Visual Hierarchy & Focus",
            "summary": (
                "Measures how clearly and efficiently the landing page directs user attention to the most important elements "
                "(hero banner, primary CTA, featured categories). A strong hierarchy presents a single dominant focal point, "
                "minimal competing distractions, and an intuitive flow from top‑priority content to supporting information."
            ),
            "scoring_criteria": [
                {
                    "name": "Primary focal point clarity",
                    "what_to_look_for": "One obvious hero/banner or headline that instantly tells users 'Start here.'",
                    "how_to_judge": "Multiple competing banners or no standout element lowers the score; a single, unmistakable focal point raises it."
                },
                {
                    "name": "CTA prominence",
                    "what_to_look_for": "Primary 'Shop Now' (or equivalent) button stands out via color, size, or position.",
                    "how_to_judge": "CTA blending into background or overshadowed by lesser items deducts points."
                },
                {
                    "name": "Clutter control",
                    "what_to_look_for": "Limited number of promotional modules, pop‑ups, animations, or sidebars.",
                    "how_to_judge": "Busy carousels, blinking offers, or dense ad areas reduce the score; restrained, purposeful content increases it."
                },
                {
                    "name": "Content grouping & flow",
                    "what_to_look_for": "Logical sequencing—hero → key categories/promotions → supportive info, with clear spacing between sections.",
                    "how_to_judge": "Erratic eye jumps or mis‑grouped elements penalize; smooth vertical or F/Z‑pattern flow rewards."
                },
                {
                    "name": "Visual emphasis techniques",
                    "what_to_look_for": "Size, color contrast, and whitespace used to rank importance.",
                    "how_to_judge": "All elements given equal weight lowers clarity; obvious hierarchy of text sizes, colors, and imagery boosts it."
                },
                {
                    "name": "Distraction management",
                    "what_to_look_for": "Minimal auto‑play videos, aggressive pop‑ups, or secondary widgets drawing focus away from the main goal.",
                    "how_to_judge": "Frequent distractions lower the score; subtle or postponed secondary elements raise it."
                }
            ],
            "scoring_guide": {
                1: {
                    "label": "Very Poor",
                    "quick_diagnostic": "Page feels chaotic; many banners scream for attention or nothing stands out; user confused where to look.",
                    "example": "Five animated promotions, auto‑rotating carousel, and no clear CTA button in first viewport."
                },
                2: {
                    "label": "Poor",
                    "quick_diagnostic": "Some structure but focus diluted by side elements or busy background; eyes jump between highlights.",
                    "example": "Hero banner exists but flanked by two sidebar promos of equal visual weight plus moving Instagram feed."
                },
                3: {
                    "label": "Average",
                    "quick_diagnostic": "Clear main area but slightly crowded; a few extra promos or spacing issues; functional yet not optimal.",
                    "example": "Large banner with headline, three secondary promos directly underneath with similar visual weight."
                },
                4: {
                    "label": "Good",
                    "quick_diagnostic": "Dominant hero, limited supplementary sections, strong CTA, ample whitespace; minor tweaks left.",
                    "example": "Full‑width seasonal sale banner, bold 'Shop Now', followed by three category tiles; no pop‑ups."
                },
                5: {
                    "label": "Excellent",
                    "quick_diagnostic": "Clean, curated layout with one primary focus, restrained secondary elements, flawless flow; feels premium.",
                    "example": "Single immersive hero for new collection, standout CTA, minimal copy, and subtle scroll cue; no distractions."
                }
            }
        },
        "primary_cta_effectiveness": {
            "title": "Primary Call‑to‑Action (CTA) Effectiveness",
            "summary": (
                "Evaluates how obvious, compelling, and easy‑to‑interact‑with the landing page’s main CTA is. "
                "Considers wording (clear benefit + action), visual distinction (button styling, contrast), placement in the page flow, "
                "and whether multiple CTAs compete or complement each other. "
                "A focused, well‑designed CTA is the main lever for pushing visitors deeper into the shopping or sign‑up funnel."
            ),
            "scoring_criteria": [
                {
                    "name": "Visibility & placement",
                    "what_to_look_for": "CTA appears in the hero or other high‑attention area; repeated sensibly on longer pages.",
                    "how_to_judge": "CTA below the fold or buried in text lowers the score; above‑the‑fold, eye‑level placement raises it."
                },
                {
                    "name": "Wording & value clarity",
                    "what_to_look_for": "Action‑oriented text that tells users what happens next or what they gain ('Shop the Sale').",
                    "how_to_judge": "Generic labels ('Submit', 'Click Here') or unclear benefits deduct points; specific, benefit‑oriented labels add points."
                },
                {
                    "name": "Visual distinction",
                    "what_to_look_for": "Button styling (size, color, padding) that sets the CTA apart from surrounding content.",
                    "how_to_judge": "CTA blending with body text or low contrast reduces score; high contrast, ample white space increases it."
                },
                {
                    "name": "Hierarchy & lack of conflict",
                    "what_to_look_for": "One primary CTA (or one per clear segment) with secondary actions visually subordinate.",
                    "how_to_judge": "Equal‑weight buttons or numerous competing CTAs cause choice paralysis and lower score; clear hierarchy boosts it."
                },
                {
                    "name": "Contextual support",
                    "what_to_look_for": "CTA placed after or alongside persuasive copy, imagery, or value proposition.",
                    "how_to_judge": "CTA appearing before explanation or requiring excessive scroll detracts; logical, timely placement enhances."
                },
                {
                    "name": "Reinforcement & repetition strategy",
                    "what_to_look_for": "CTA echoed at logical breakpoints on long pages without feeling spammy.",
                    "how_to_judge": "Missing secondary placements or excessive repetition (every screen) deduct; well‑timed repeats add."
                }
            ],
            "scoring_guide": {
                1: {
                    "label": "Very Poor",
                    "quick_diagnostic": "CTA missing, hidden, or lost among many buttons; user unsure how to proceed.",
                    "example": "Welcome text only; 'Shop Now' buried in a carousel slide that rotates away."
                },
                2: {
                    "label": "Poor",
                    "quick_diagnostic": "A CTA exists but label is vague or looks like plain text; odd placement; multiple equal buttons create confusion.",
                    "example": "'Submit' button in footer before any details; three identically styled CTAs for different actions."
                },
                3: {
                    "label": "Average",
                    "quick_diagnostic": "Obvious 'Shop Now' in hero with contrasting color; some secondary CTAs slightly distract; could be more prominent.",
                    "example": "Hero button stands out, but sidebar 'Join Newsletter' link competes visually."
                },
                4: {
                    "label": "Good",
                    "quick_diagnostic": "Action‑oriented, benefit‑driven label; strong design contrast; intuitive placement; minimal competing links.",
                    "example": "Bold 'Get 10% Off – Shop Sale' button front‑and‑center, repeated once mid‑page."
                },
                5: {
                    "label": "Excellent",
                    "quick_diagnostic": "Singular, irresistible CTA aligned with business goal; perfect contrast; directional cues; zero conflict.",
                    "example": "Fullscreen hero with 'Claim Your Discount' button, arrow icon drawing eye, nav minimized; second identical button near fold."
                }
            }
        },
        "product_discovery_category_highlights": {
            "title": "Product Discovery & Category Highlights",
            "summary": (
                "Examines how effectively the homepage exposes users to the breadth of the catalog and offers clear, enticing pathways "
                "into key categories, promotions, or featured products. Focus is on visibility, relevance, organization, and inspiration: "
                "does the page feel like a curated storefront window that quickly answers “What can I shop here?” and nudges users toward "
                "popular or strategic sections?"
            ),
            "scoring_criteria": [
                {
                    "name": "Category visibility & labeling",
                    "what_to_look_for": "Prominent tiles, links, or icons for major product categories with concise, intuitive names.",
                    "how_to_judge": "Omitted or cryptic category links lower score; clearly labeled, visually distinct categories raise it."
                },
                {
                    "name": "Strategic prioritization",
                    "what_to_look_for": "Highlighted categories/products align with seasonality, popularity, or business goals (e.g., high‑margin, new arrivals).",
                    "how_to_judge": "Random or niche first impressions deduct points; timely, high‑interest selections add points."
                },
                {
                    "name": "Layout clarity & balance",
                    "what_to_look_for": "Clean grid, carousel, or sectioned layout that avoids overwhelming lists.",
                    "how_to_judge": "Massive unstructured link lists or cluttered promo blocks reduce score; balanced presentation boosts it."
                },
                {
                    "name": "Featured product enticement",
                    "what_to_look_for": "High‑quality images and clear context (e.g., 'Trending', 'New In') for showcased items.",
                    "how_to_judge": "Low‑resolution images or unlabeled product grids detract; compelling imagery and labels enhance."
                },
                {
                    "name": "Guidance to next step",
                    "what_to_look_for": "Obvious CTAs or links within each highlighted area directing users deeper (e.g., 'Shop Electronics').",
                    "how_to_judge": "Category tile without follow‑up link or vague 'Learn More' lowers score; direct, action‑oriented links raise it."
                },
                {
                    "name": "Personalization / discovery aids (advanced)",
                    "what_to_look_for": "Dynamic recommendations, quizzes, or search examples that tailor discovery.",
                    "how_to_judge": "None expected for mid‑tier sites, but presence of smart aids can lift score to top tier."
                }
            ],
            "scoring_guide": {
                1: {
                    "label": "Very Poor",
                    "quick_diagnostic": "No category showcase; homepage is a generic welcome with no product glimpses or only one vague 'Browse Catalog' link.",
                    "example": "Full‑screen hero video, minimal text, no tiles or product images; user must open nav to see categories."
                },
                2: {
                    "label": "Poor",
                    "quick_diagnostic": "Attempts at discovery but ineffective—oversized list of 30 text links or irrelevant categories; little context.",
                    "example": "Sidebar list 'Stationery, Pet Supplies, Car Parts…' with no images; hard to know where to start."
                },
                3: {
                    "label": "Average",
                    "quick_diagnostic": "Basic grid of 6–8 main categories or a 'Featured Products' row; adequate but not strategic or comprehensive.",
                    "example": "Tiles for 'Men', 'Women', 'Kids', but missing popular 'Sale' or 'New In' sections."
                },
                4: {
                    "label": "Good",
                    "quick_diagnostic": "Well‑designed section for top categories, plus 'Trending' or seasonal promo; visually appealing and organized.",
                    "example": "Three large tiles ('Spring Sale', 'Electronics', 'Home & Garden') with clear imagery and CTAs, plus 'New Arrivals' carousel."
                },
                5: {
                    "label": "Excellent",
                    "quick_diagnostic": "Curated mix of popular, new, and seasonal highlights; possibly personalized; interactive aids guide every shopper.",
                    "example": "Personalized 'Recommended for You' strip, major category tiles with sub‑links, holiday gift guide banner—all harmonious and uncluttered."
                }
            }
        }
    },
    "search": {
        "listing_content_info_density": {
            "title": "Product Listing Content & Information Density",
            "summary": (
                "Rates how much and how well information is presented on each product card in the results list. "
                "Balances completeness (name, image, price, variations, ratings, stock, promos) against scannability—"
                "enough details to compare, no overwhelming clutter. Well‑tuned listings let shoppers shortlist accurately, "
                "raising click‑through quality and conversion."
            ),
            "scoring_criteria": [
                {
                    "name": "Essential info completeness",
                    "what_to_look_for": "Every product shows at minimum a clear image, full name, and price.",
                    "how_to_judge": "Missing any of these for some items lowers the score; consistently present raises it."
                },
                {
                    "name": "Helpful add‑ons",
                    "what_to_look_for": "Ratings, review count, promo badges ('Sale', 'New'), free‑shipping tag, urgency ('Only 2 left').",
                    "how_to_judge": "Lack of relevant cues deducts points; thoughtful, concise extras add points."
                },
                {
                    "name": "Variation indicators",
                    "what_to_look_for": "Color swatches, '5 sizes', or text hinting multiple options when important to purchase.",
                    "how_to_judge": "No hint about variants that matter lowers score; clear, space‑saving indicators raise it."
                },
                {
                    "name": "Visual clarity & consistency",
                    "what_to_look_for": "Adequate image size, proper cropping, readable titles (no excessive truncation).",
                    "how_to_judge": "Tiny or misaligned images, cut‑off names, inconsistent layouts reduce score; crisp, uniform cards add points."
                },
                {
                    "name": "Information density & layout",
                    "what_to_look_for": "Clean card/grid with hierarchy—key data emphasized, secondary info subdued.",
                    "how_to_judge": "Overly busy cards or massive whitespace deduct; balanced text/icon mix boosts."
                },
                {
                    "name": "Decision aids / interactivity (advanced)",
                    "what_to_look_for": "Quick‑view, add‑to‑cart or wishlist from listing, hover zoom, compare checkbox.",
                    "how_to_judge": "Absent is fine for mid‑tier scores; well‑implemented aids can lift to top tier."
                }
            ],
            "scoring_guide": {
                1: {
                    "label": "Very Poor",
                    "quick_diagnostic": "Only product names as links or name + image, no price; user must click each item blindly.",
                    "example": "Text list of 'Model A', 'Model B' with no photos or prices."
                },
                2: {
                    "label": "Poor",
                    "quick_diagnostic": "Image, name, price for some items; missing or inconsistent info; small, unclear images.",
                    "example": "Half the TVs show price, others 'See price in cart'; ratings absent; thumbnails tiny."
                },
                3: {
                    "label": "Average",
                    "quick_diagnostic": "Image, full name, price on all items; maybe basic star rating; scannable but minimal extras.",
                    "example": "Clothing grid with photo, title, price; no color or size hints."
                },
                4: {
                    "label": "Good",
                    "quick_diagnostic": "Clear images, descriptive titles, price + discounts, ratings, variant hints; uncluttered layout.",
                    "example": "Laptop listings with large photo, '13‑inch, 256 GB', price + 'SAVE 15%', ★4.5 and review count."
                },
                5: {
                    "label": "Excellent",
                    "quick_diagnostic": "Rich yet clean cards—price, discount %, ratings, stock/urgency, variant swatches, quick‑view/add‑to‑cart; still easy to scan.",
                    "example": "Sneakers grid with hover quick‑view, color dots, 'Only 2 left!', strike‑through old price, ★4.8; card stays tidy."
                }
            }
        },
        "filtering_sorting_functionality": {
            "title": "Filtering & Sorting Functionality",
            "summary": (
                "Measures how completely and effortlessly users can narrow or reorder a long list of products. "
                "Focus areas: breadth and relevance of filters, ease of interaction (multi‑select, instant update), "
                "visibility of active filters, result counts, and variety of sort options. Effective tools shorten time‑to‑product, "
                "reduce frustration, and drive higher conversion."
            ),
            "scoring_criteria": [
                {
                    "name": "Filter range & relevance",
                    "what_to_look_for": "Facets that match the product category (e.g., size, color for apparel; brand, screen size for TVs).",
                    "how_to_judge": "Missing key facets lowers score; comprehensive, context‑specific facets raise it."
                },
                {
                    "name": "Filter UI usability",
                    "what_to_look_for": "Familiar controls (checkboxes, sliders), clear labels, ability to multi‑select and combine filters.",
                    "how_to_judge": "One‑at‑a‑time selection or hard‑to‑tap controls deduct; intuitive multi‑select adds."
                },
                {
                    "name": "Speed & feedback",
                    "what_to_look_for": "Instant or AJAX updates, visible loading indicators, real‑time result counts.",
                    "how_to_judge": "Full page reloads or no feedback lower score; live counts & instant refresh raise."
                },
                {
                    "name": "Active filter management",
                    "what_to_look_for": "Tags, chips, or summary bar showing applied filters with easy remove/reset actions.",
                    "how_to_judge": "Hidden active filters or complex removal penalize; clear, one‑click removal boosts."
                },
                {
                    "name": "Sorting breadth & clarity",
                    "what_to_look_for": "Options for price, newest, popularity, rating, etc., via dropdown or buttons.",
                    "how_to_judge": "Only one sort criterion or confusing labels lower score; diverse, obvious options raise."
                },
                {
                    "name": "Advanced aids (top‑tier)",
                    "what_to_look_for": "Search within filters, adaptive facets, disabling zero‑result options, remembered sort prefs.",
                    "how_to_judge": "Absence fine for mid‑tier; presence of smart aids can elevate to level 5."
                }
            ],
            "scoring_guide": {
                1: {
                    "label": "Very Poor",
                    "quick_diagnostic": "No filters or sorting; user must scroll through hundreds of items.",
                    "example": "Results list 1,000 phones with no sidebar or sort dropdown."
                },
                2: {
                    "label": "Poor",
                    "quick_diagnostic": "Few generic filters, clunky interface, single‑select only, slow reloads; limited sort.",
                    "example": "Dropdown 'Brand' resets page on each pick; only 'Price' sort available."
                },
                3: {
                    "label": "Average",
                    "quick_diagnostic": "Standard multi‑select filters and basic sorts; page reload on apply; counts after filtering.",
                    "example": "Sidebar with size, color, price; click 'Apply' reloads page; sort by price or newest."
                },
                4: {
                    "label": "Good",
                    "quick_diagnostic": "Comprehensive, instant filters with result counts; removable filter tags; several sort options.",
                    "example": "Check three colors & one size, list updates instantly; dropdown sort by rating, popularity, price."
                },
                5: {
                    "label": "Excellent",
                    "quick_diagnostic": "Adaptive, real‑time filters with live counts, search‑within‑facet, zero‑result options disabled; remembers sort.",
                    "example": "Electronics results show only relevant specs filters, live counts update as user types '128 GB' in storage filter search; sticky sort bar remembers 'Lowest price'."
                }
            }
        }
    },
    "product": {
        "product_info_description_quality": {
            "title": "Product Information & Description Quality",
            "summary": (
                "Assesses how thoroughly and clearly the product page explains the item: description narrative, spec list, "
                "size/dimension info, materials, usage, unique selling points, and supporting assets. Evaluates clarity of writing, "
                "logical organization (tabs, bullets, accordions), and accessibility of every detail a shopper needs to feel confident."
            ),
            "scoring_criteria": [
                {
                    "name": "Core detail completeness",
                    "what_to_look_for": "Title, descriptive paragraph, key specs (size, material, function), price and what’s included.",
                    "how_to_judge": "Missing any core detail lowers score; fully covered basics raise it."
                },
                {
                    "name": "Organization & readability",
                    "what_to_look_for": "Logical sections (Description, Specs, Reviews, Q&A), bulleted lists, headings.",
                    "how_to_judge": "Wall‑of‑text or scattered info deduct; tidy sections & bullets add."
                },
                {
                    "name": "Clarity & tone",
                    "what_to_look_for": "Jargon‑free language, concise yet informative, benefits highlighted.",
                    "how_to_judge": "Marketing fluff or tech jargon without explanation reduces; clear, user‑centric copy boosts."
                },
                {
                    "name": "Depth of specifications / FAQs",
                    "what_to_look_for": "Detailed spec table, size charts, compatibility notes, care instructions.",
                    "how_to_judge": "Key specs omitted or vague deduct; thorough spec coverage raise."
                },
                {
                    "name": "Differentiators & unique selling points",
                    "what_to_look_for": "Highlights of what makes this product stand out (e.g., eco‑friendly, patented tech).",
                    "how_to_judge": "No differentiation info lowers; clear USPs elevate."
                },
                {
                    "name": "Supplementary assets",
                    "what_to_look_for": "Manuals, ingredient lists, comparison charts, downloadable guides.",
                    "how_to_judge": "None expected for mid‑tier; rich assets can push to top tier."
                }
            ],
            "scoring_guide": {
                1: {
                    "label": "Very Poor",
                    "quick_diagnostic": "Title + single vague sentence; no specs, sizes, or materials.",
                    "example": "“Handbag – stylish and durable.” (no dimensions, material, pockets info)."
                },
                2: {
                    "label": "Poor",
                    "quick_diagnostic": "Short paragraph but missing critical details or buried deep; jargon heavy.",
                    "example": "Laptop page lists CPU but no RAM/storage; specs hidden in collapsed section below fold."
                },
                3: {
                    "label": "Average",
                    "quick_diagnostic": "Basic paragraph + bullet specs covering size, material, main features; no extras.",
                    "example": "T‑shirt page lists fabric, available sizes, care instructions; no size chart image."
                },
                4: {
                    "label": "Good",
                    "quick_diagnostic": "Engaging description, full spec table, size chart, compatibility notes; clear layout.",
                    "example": "Camera page with bullet USPs, detailed specs tab, downloadable manual link."
                },
                5: {
                    "label": "Excellent",
                    "quick_diagnostic": "Comprehensive multi‑section info incl. highlights, spec table, FAQs, comparison chart, manuals; easy to scan.",
                    "example": "High‑end phone page with “Top 5 features” bullets, full tech sheet, “Compare models” chart, warranty PDF."
                }
            }
        },
        "product_imagery_media": {
            "title": "Product Imagery & Media",
            "summary": (
                "Assesses the quality, diversity, and usefulness of product visuals on the product page. "
                "Covers image resolution, variety of angles, in-context or lifestyle imagery, zoom functionality, and inclusion of video or 360° media."
            ),
            "scoring_criteria": [
                {
                    "name": "Variety of imagery",
                    "what_to_look_for": "Multiple angles, zoomed-in shots, in-use scenarios.",
                    "how_to_judge": "Single static photo or duplicate angles reduce score; diverse visuals raise it."
                },
                {
                    "name": "Image quality",
                    "what_to_look_for": "High-resolution, properly cropped, color-accurate images.",
                    "how_to_judge": "Pixelated, blurry, or poorly lit images deduct points; crisp, vivid images reward."
                },
                {
                    "name": "Zoom or enlarge functionality",
                    "what_to_look_for": "Hover zoom, click-to-enlarge, or pinch support on mobile.",
                    "how_to_judge": "No zoom capability or broken zoom features lower score; intuitive zoom raises it."
                },
                {
                    "name": "Media types (static vs dynamic)",
                    "what_to_look_for": "Videos, 360° views, or animation showing product in action.",
                    "how_to_judge": "No dynamic media fine for mid-scores; good usage elevates to top."
                },
                {
                    "name": "Real-world context",
                    "what_to_look_for": "Product shown in lifestyle scenarios (e.g., on model, in room).",
                    "how_to_judge": "No in-use context images lower the score; realistic use visuals raise it."
                }
            ],
            "scoring_guide": {
                1: {
                    "label": "Very Poor",
                    "quick_diagnostic": "Only one photo, low quality, no zoom, no lifestyle shots.",
                    "example": "Flat lay of handbag on white with no alternate views or details."
                },
                2: {
                    "label": "Poor",
                    "quick_diagnostic": "Few photos, awkward angles, no zoom; possibly off-brand or stock images.",
                    "example": "Two images of a blender from odd perspectives, grainy, no zoom."
                },
                3: {
                    "label": "Average",
                    "quick_diagnostic": "Acceptable quality, front/back/side photos, no dynamic media or in-use shots.",
                    "example": "Shirt with three photos, decent clarity, but nothing showing fit or styling."
                },
                4: {
                    "label": "Good",
                    "quick_diagnostic": "Multiple clean images, some context or zoom, consistent style.",
                    "example": "Sneakers with top, side, back, on-foot image, and pinch-to-zoom on mobile."
                },
                5: {
                    "label": "Excellent",
                    "quick_diagnostic": "Hi-res gallery with zoom, lifestyle photos, video, and/or 360° view.",
                    "example": "Smartwatch page with rotating 360°, zoom, on-wrist lifestyle image, and demo video."
                }
            }
        },
        "product_card_pricing_availability": {
            "title": "Product Cart",
            "summary": (
                "Measures how clearly the product page communicates cost, stock, and purchase actions, "
                "and how effectively it encourages completing or expanding the cart through smart recommendations. "
                "Combines pricing visibility, add-to-cart UX, and related product suggestions."
            ),
            "scoring_criteria": [
                {
                    "name": "Price clarity & savings visibility",
                    "what_to_look_for": "High-contrast price near title; sale strikes/percent saved; no hidden costs.",
                    "how_to_judge": "Unclear, buried, or misleading prices lower the score; bold, transparent savings info raises it."
                },
                {
                    "name": "Availability & urgency cues",
                    "what_to_look_for": "Clear 'In stock / Out of stock / Pre-order' labels; urgency tags like 'Only 2 left'.",
                    "how_to_judge": "Missing or vague stock info lowers score; clear real-time status raises it."
                },
                {
                    "name": "Variant-aware updates",
                    "what_to_look_for": "Prices and stock that update with selected size/color; unavailable options grayed out.",
                    "how_to_judge": "Static or error-prone variants reduce score; dynamic behavior boosts it."
                },
                {
                    "name": "CTA prominence & usability",
                    "what_to_look_for": "Stand-out 'Add to Cart' button with logical placement and mobile accessibility.",
                    "how_to_judge": "Hidden or awkward CTAs lower the score; bold, consistent, mobile-friendly CTAs raise it."
                },
                {
                    "name": "Selection & quantity controls",
                    "what_to_look_for": "Clear dropdowns, swatches, +/- buttons with proper error handling.",
                    "how_to_judge": "Confusing or glitchy controls lower score; intuitive selection flow raises it."
                },
                {
                    "name": "Post-add feedback",
                    "what_to_look_for": "Mini-cart updates, toast confirmations, cart badge refresh.",
                    "how_to_judge": "No visible feedback lowers score; instant confirmation raises it."
                },
                {
                    "name": "Relevancy of related/cross-sell items",
                    "what_to_look_for": "Suggested items closely tied to the product (accessories, bundles, similar styles).",
                    "how_to_judge": "Random or unrelated suggestions lower the score; targeted upsells raise it."
                },
                {
                    "name": "Cross-sell UI & actionability",
                    "what_to_look_for": "Scroll-friendly carousel or grid; one-click add, quick-view options.",
                    "how_to_judge": "Hard-to-navigate, non-interactive UI lowers score; snappy experience boosts it."
                },
                {
                    "name": "Advanced personalization / fulfillment info",
                    "what_to_look_for": "Location-aware delivery times, store availability, bundle/financing info.",
                    "how_to_judge": "Missing extras is fine for mid-tier; personalized delivery/promos elevate to top."
                }
            ],
            "scoring_guide": {
                1: {
                    "label": "Very Poor",
                    "quick_diagnostic": "Price hidden until cart; no stock info; weak or missing Add button; zero relevant suggestions.",
                    "example": "“Add to cart to see price”; user discovers 'Out of stock' after trying to check out."
                },
                2: {
                    "label": "Poor",
                    "quick_diagnostic": "Price exists but tiny; unclear sale context; off-brand suggestions; difficult CTA.",
                    "example": "Grey 'Add' link under fold; irrelevant item suggestions like lamp with sneakers."
                },
                3: {
                    "label": "Average",
                    "quick_diagnostic": "Decent price + strike-through; variant prompts; default accessories row.",
                    "example": "Shirt with price updating by size, standard 'You may also like' carousel."
                },
                4: {
                    "label": "Good",
                    "quick_diagnostic": "Sticky bold price; variant-controlled stock; well-placed Add button and bundles.",
                    "example": "“Only 3 left” next to price; laptop + sleeve + mouse bundle below CTA."
                },
                5: {
                    "label": "Excellent",
                    "quick_diagnostic": "Live stock per location, delivery ETA; mini-cart feedback; hyper-relevant cross-sells.",
                    "example": "Camera with countdown timer, instant variant price updates, AI-recommended accessories."
                }
            }
        }
    }
}
