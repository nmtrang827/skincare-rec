export const quiz = [
    {
        id: "acne_frequency",
        category: "Acne_Severity",
        weight: 0.6,

        question: "How often do you get pimples or breakouts?",

        answers: [
            { text: "Rarely or never", value: 0 },
            { text: "A few times a year", value: 2 },
            { text: "About once a month", value: 5 },
            { text: "Almost every week", value: 8 },
            { text: "Almost always", value: 10 }
        ]
    },

    {
        id: "acne_severity",
        category: "Acne_Severity",
        weight: 0.4,

        question: "When you break out, how severe are they usually?",

        answers: [
            { text: "Small whiteheads only", value: 2 },
            { text: "A few pimples", value: 4 },
            { text: "Several inflamed pimples", value: 7 },
            { text: "Painful cystic acne", value: 10 }
        ]
    },

    {
        id: "dry_after_wash",
        category: "Dryness_Severity",
        weight: 0.7,

        question: "How does your skin feel after washing your face?",

        answers: [
            { text: "Comfortable", value: 0 },
            { text: "Slightly tight", value: 3 },
            { text: "Noticeably tight", value: 6 },
            { text: "Very tight", value: 8 },
            { text: "Flaky or peeling", value: 10 }
        ]
    },

    {
        id: "dry_midday_shine",
        category: "Dryness_Severity",
        weight: 0.3,

        question: "By the middle of the day, how shiny does your face usually become?",

        answers: [
            { text: "Very shiny", value: 0 },
            { text: "Somewhat shiny", value: 2 },
            { text: "A little shiny", value: 5 },
            { text: "Barely shiny", value: 8 },
            { text: "Never shiny", value: 10 }
        ]
    },

    {
        id: "sensitive_new_products",
        category: "Sensitivity_Severity",
        weight: 0.5,

        question: "How often does your skin sting or burn after trying new skincare products?",

        answers: [
            { text: "Never", value: 0 },
            { text: "Rarely", value: 2 },
            { text: "Sometimes", value: 5 },
            { text: "Often", value: 8 },
            { text: "Almost always", value: 10 }
        ]
    },

    {
        id: "sensitive_redness",
        category: "Sensitivity_Severity",
        weight: 0.5,

        question: "How easily does your skin become red or irritated?",

        answers: [
            { text: "Very rarely", value: 0 },
            { text: "Occasionally", value: 3 },
            { text: "Sometimes", value: 5 },
            { text: "Often", value: 8 },
            { text: "Very easily", value: 10 }
        ]
    },

    {
        id: "pigment_post_acne",
        category: "Pigmentation_Severity",
        weight: 0.6,

        question: "After a pimple heals, how often does it leave a dark mark?",

        answers: [
            { text: "Never", value: 0 },
            { text: "Occasionally", value: 3 },
            { text: "Sometimes", value: 6 },
            { text: "Most of the time", value: 8 },
            { text: "Almost always", value: 10 }
        ]
    },

    {
        id: "pigment_uneven_tone",
        category: "Pigmentation_Severity",
        weight: 0.4,

        question: "How uneven is your overall skin tone?",

        answers: [
            { text: "Very even", value: 0 },
            { text: "Slightly uneven", value: 3 },
            { text: "Moderately uneven", value: 6 },
            { text: "Quite uneven", value: 8 },
            { text: "Very uneven", value: 10 }
        ]
    },

    {
        id: "aging_fine_lines",
        category: "Aging_Severity",
        weight: 0.8,

        question: "How noticeable are fine lines or wrinkles on your face?",

        answers: [
            { text: "None", value: 0 },
            { text: "Very slight", value: 2 },
            { text: "Some noticeable fine lines", value: 5 },
            { text: "Several visible wrinkles", value: 8 },
            { text: "Deep wrinkles", value: 10 }
        ]
    },

    {
        id: "aging_firmness",
        category: "Aging_Severity",
        weight: 0.2,

        question: "How would you describe your skin's firmness and elasticity?",

        answers: [
            { text: "Very firm", value: 0 },
            { text: "Mostly firm", value: 2 },
            { text: "Slightly less firm", value: 5 },
            { text: "Noticeably less firm", value: 8 },
            { text: "Very loose or sagging", value: 10 }
        ]
    },
];