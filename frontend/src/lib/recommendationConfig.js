// Purpose: Define curriculum schemas, interest options, and preference dimensions for dynamic Apti intake.
// Callers: RecommendationJourney and result shaping logic.
// Deps: None.
// API: Exported trackConfig, interestOptions, preferenceGroups, and helpers.
// Side effects: None.
export const trackConfig = {
  IPA: {
    label: { en: 'IPA', id: 'IPA' },
    curriculumType: 'ipa',
    requiredSubjects: [
      ['religion', 'Pendidikan Agama'],
      ['civics', 'PPKn'],
      ['indonesian', 'Bahasa Indonesia'],
      ['english', 'Bahasa Inggris'],
      ['general_math', 'Matematika Umum'],
      ['pjok', 'PJOK'],
      ['arts', 'Seni'],
      ['biology', 'Biologi'],
      ['physics', 'Fisika'],
      ['chemistry', 'Kimia'],
      ['advanced_math', 'Matematika Peminatan']
    ],
    optionalSubjects: [['informatics', 'Informatika']]
  },
  IPS: {
    label: { en: 'IPS', id: 'IPS' },
    curriculumType: 'ips',
    requiredSubjects: [
      ['religion', 'Pendidikan Agama'],
      ['civics', 'PPKn'],
      ['indonesian', 'Bahasa Indonesia'],
      ['english', 'Bahasa Inggris'],
      ['general_math', 'Matematika Umum'],
      ['pjok', 'PJOK'],
      ['arts', 'Seni'],
      ['sociology', 'Sosiologi'],
      ['geography', 'Geografi'],
      ['economics', 'Ekonomi'],
      ['history', 'Sejarah']
    ],
    optionalSubjects: [['informatics', 'Informatika']]
  },
  Bahasa: {
    label: { en: 'Bahasa', id: 'Bahasa' },
    curriculumType: 'bahasa',
    requiredSubjects: [
      ['religion', 'Pendidikan Agama'],
      ['civics', 'PPKn'],
      ['basic_math', 'Matematika Dasar'],
      ['history', 'Sejarah'],
      ['indonesian_literature', 'Bahasa dan Sastra Indonesia'],
      ['english_literature', 'Bahasa dan Sastra Inggris'],
      ['anthropology', 'Antropologi']
    ],
    optionalSubjects: [
      ['foreign_language_arabic', 'Bahasa Asing: Arab'],
      ['foreign_language_japanese', 'Bahasa Asing: Jepang'],
      ['foreign_language_german', 'Bahasa Asing: Jerman'],
      ['foreign_language_mandarin', 'Bahasa Asing: Mandarin'],
      ['foreign_language_french', 'Bahasa Asing: Prancis'],
      ['foreign_literature', 'Sastra Asing']
    ]
  },
  Merdeka: {
    label: { en: 'Kurikulum Merdeka', id: 'Kurikulum Merdeka' },
    curriculumType: 'merdeka',
    requiredSubjects: [
      ['religion', 'Pendidikan Agama'],
      ['pancasila', 'Pancasila'],
      ['indonesian', 'Bahasa Indonesia'],
      ['math', 'Matematika'],
      ['english', 'Bahasa Inggris'],
      ['pjok', 'PJOK'],
      ['arts', 'Seni']
    ],
    optionalSubjects: [['informatics', 'Informatika']],
    electiveSubjects: [
      ['biology', 'Biologi'],
      ['chemistry', 'Kimia'],
      ['physics', 'Fisika'],
      ['advanced_math', 'Matematika Lanjut'],
      ['sociology', 'Sosiologi'],
      ['economics', 'Ekonomi'],
      ['geography', 'Geografi'],
      ['anthropology', 'Antropologi'],
      ['advanced_language', 'Bahasa Lanjut'],
      ['foreign_language', 'Bahasa Asing'],
      ['entrepreneurship', 'Kewirausahaan']
    ]
  }
};

export const interestOptions = [
  'Technology',
  'Engineering',
  'Health',
  'Business',
  'Social',
  'Law',
  'Education',
  'Psychology',
  'Media',
  'Design',
  'Language',
  'Environment',
  'Data / AI'
];

export const preferenceGroups = {
  orientation: ['Numbers', 'People', 'Creativity'],
  approach: ['Technical', 'Social'],
  style: ['Teamwork', 'Independent']
};

export function buildInitialScores(trackKey) {
  const track = trackConfig[trackKey];
  const subjectKeys = [
    ...(track?.requiredSubjects || []).map(([key]) => key),
    ...(track?.optionalSubjects || []).map(([key]) => key)
  ];

  return Object.fromEntries(subjectKeys.map((key) => [key, '']));
}
