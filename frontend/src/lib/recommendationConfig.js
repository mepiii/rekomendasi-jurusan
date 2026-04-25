// Purpose: Define curriculum schemas, interest options, and preference dimensions for dynamic Apti intake.
// Callers: RecommendationJourney and result shaping logic.
// Deps: None.
// API: Exported trackConfig, interestOptions, preferenceGroups, prodiIntakeSteps, and helpers.
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
    optionalSubjects: [['informatics', 'Informatika'], ['prakarya', 'Prakarya']]
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
    optionalSubjects: [['informatics', 'Informatika'], ['prakarya', 'Prakarya']]
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
      ['prakarya', 'Prakarya'],
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
    optionalSubjects: [['informatics', 'Informatika'], ['prakarya', 'Prakarya']],
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
  { value: 'Technology', label: { en: 'Technology', id: 'Teknologi' } },
  { value: 'Engineering', label: { en: 'Engineering', id: 'Teknik' } },
  { value: 'Health', label: { en: 'Health', id: 'Kesehatan' } },
  { value: 'Business', label: { en: 'Business', id: 'Bisnis' } },
  { value: 'Social', label: { en: 'Social', id: 'Sosial' } },
  { value: 'Law', label: { en: 'Law', id: 'Hukum' } },
  { value: 'Education', label: { en: 'Education', id: 'Pendidikan' } },
  { value: 'Psychology', label: { en: 'Psychology', id: 'Psikologi' } },
  { value: 'Media', label: { en: 'Media', id: 'Media' } },
  { value: 'Design', label: { en: 'Design', id: 'Desain' } },
  { value: 'Language', label: { en: 'Language', id: 'Bahasa' } },
  { value: 'Environment', label: { en: 'Environment', id: 'Lingkungan' } },
  { value: 'Data / AI', label: { en: 'Data / AI', id: 'Data / AI' } }
];

export const preferenceGroups = {
  orientation: [
    { value: 'Numbers', label: { en: 'Numbers', id: 'Angka' } },
    { value: 'People', label: { en: 'People', id: 'Manusia' } },
    { value: 'Creativity', label: { en: 'Creativity', id: 'Kreativitas' } }
  ],
  approach: [
    { value: 'Technical', label: { en: 'Technical', id: 'Teknis' } },
    { value: 'Social', label: { en: 'Social', id: 'Sosial' } }
  ],
  style: [
    { value: 'Teamwork', label: { en: 'Teamwork', id: 'Kerja tim' } },
    { value: 'Independent', label: { en: 'Independent', id: 'Mandiri' } }
  ]
};

export const religionRelatedMajorPreferences = [
  { value: 'Not relevant', label: { en: 'Not relevant', id: 'Tidak relevan' } },
  { value: 'Avoid religion-related majors', label: { en: 'Avoid religion-related majors', id: 'Hindari jurusan terkait agama' } },
  { value: 'Open to religion-related majors', label: { en: 'Open to religion-related majors', id: 'Terbuka untuk jurusan terkait agama' } },
  { value: 'Prefer religion-related majors', label: { en: 'Prefer religion-related majors', id: 'Prioritaskan jurusan terkait agama' } }
];

export const prodiIntakeSteps = [
  { key: 'academic_context', required: true, label: { en: 'Academic context', id: 'Konteks akademik' }, helper: { en: 'Describe classes, projects, or academic signals that should shape your program recommendation.', id: 'Ceritakan kelas, proyek, atau sinyal akademik yang perlu memengaruhi rekomendasi prodi.' }, placeholder: { en: 'Example: strong STEM classes, coding club, biology olympiad...', id: 'Contoh: kuat di STEM, klub coding, olimpiade biologi...' } },
  { key: 'subject_preferences', required: true, label: { en: 'Subject preferences', id: 'Preferensi mapel' }, helper: { en: 'Which subjects do you want more or less of in college?', id: 'Mapel apa yang ingin lebih banyak atau lebih sedikit kamu temui saat kuliah?' }, placeholder: { en: 'Example: more computing and math, less memorization...', id: 'Contoh: lebih banyak komputasi dan matematika, minim hafalan...' } },
  { key: 'interest_deep_dive', required: true, label: { en: 'Interest deep dive', id: 'Pendalaman minat' }, helper: { en: 'Add specifics behind your selected interests.', id: 'Tambahkan detail dari minat yang kamu pilih.' }, placeholder: { en: 'Example: AI products, UX research, public health...', id: 'Contoh: produk AI, riset UX, kesehatan masyarakat...' } },
  { key: 'career_direction', required: true, label: { en: 'Career direction', id: 'Arah karier' }, helper: { en: 'Share career roles, work settings, or impact areas you are considering.', id: 'Tuliskan peran, lingkungan kerja, atau dampak karier yang kamu pertimbangkan.' }, placeholder: { en: 'Example: software engineer, analyst, doctor, entrepreneur...', id: 'Contoh: software engineer, analis, dokter, wirausaha...' } },
  { key: 'constraints', required: true, label: { en: 'Constraints', id: 'Batasan' }, helper: { en: 'Mention location, cost, family, duration, or study-style constraints.', id: 'Sebutkan batasan lokasi, biaya, keluarga, durasi, atau gaya belajar.' }, placeholder: { en: 'Example: prefer Jakarta, avoid long clinical path...', id: 'Contoh: prefer Jakarta, hindari jalur klinis panjang...' } },
  { key: 'expected_prodi', required: false, label: { en: 'Expected prodi', id: 'Prodi yang diharapkan' }, helper: { en: 'Optional. Add programs you already expect or want to compare.', id: 'Opsional. Tambahkan prodi yang sudah kamu harapkan atau ingin bandingkan.' }, placeholder: { en: 'Example: Informatics, Psychology...', id: 'Contoh: Informatika, Psikologi...' } },
  { key: 'prodi_to_avoid', required: false, label: { en: 'Prodi to avoid', id: 'Prodi yang dihindari' }, helper: { en: 'Optional. Add programs Apti should avoid unless strongly justified.', id: 'Opsional. Tambahkan prodi yang sebaiknya dihindari kecuali sangat kuat alasannya.' }, placeholder: { en: 'Example: Medicine, Accounting...', id: 'Contoh: Kedokteran, Akuntansi...' } },
  { key: 'free_text_goal', required: false, label: { en: 'Free-text goal', id: 'Tujuan bebas' }, helper: { en: 'Optional. Add any final context in your own words.', id: 'Opsional. Tambahkan konteks akhir dengan kata-katamu sendiri.' }, placeholder: { en: 'Example: I want a stable career but still creative...', id: 'Contoh: ingin karier stabil tapi tetap kreatif...' } }
];

export function buildInitialScores(trackKey) {
  const track = trackConfig[trackKey];
  const subjectKeys = [
    ...(track?.requiredSubjects || []).map(([key]) => key),
    ...(track?.optionalSubjects || []).map(([key]) => key)
  ];

  return Object.fromEntries(subjectKeys.map((key) => [key, '']));
}
