// Purpose: Define curriculum schemas, interest options, and preference dimensions for dynamic Apti intake.
// Callers: RecommendationJourney and result shaping logic.
// Deps: None.
// API: Exported trackConfig, interestOptions, preferenceGroups, prodiIntakeSteps, and helpers.
// Side effects: None.
export const trackConfig = {
  IPA: {
    label: { en: 'Science (IPA)', id: 'IPA' },
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
      ['advanced_math', 'Matematika Lanjut']
    ],
    optionalSubjects: [['informatics', 'Informatika'], ['prakarya', 'Prakarya']]
  },
  IPS: {
    label: { en: 'Social Studies (IPS)', id: 'IPS' },
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
    label: { en: 'Language', id: 'Bahasa' },
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
    label: { en: 'Independent Curriculum', id: 'Kurikulum Merdeka' },
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
      ['biology', { en: 'Biology', id: 'Biologi' }],
      ['chemistry', { en: 'Chemistry', id: 'Kimia' }],
      ['physics', { en: 'Physics', id: 'Fisika' }],
      ['advanced_math', { en: 'Advanced Math', id: 'Matematika Lanjut' }],
      ['sociology', { en: 'Sociology', id: 'Sosiologi' }],
      ['economics', { en: 'Economics', id: 'Ekonomi' }],
      ['geography', { en: 'Geography', id: 'Geografi' }],
      ['anthropology', { en: 'Anthropology', id: 'Antropologi' }],
      ['advanced_language', { en: 'Advanced Language', id: 'Bahasa Lanjut' }],
      ['foreign_language', { en: 'Foreign Language', id: 'Bahasa Asing' }],
      ['entrepreneurship', { en: 'Entrepreneurship', id: 'Kewirausahaan' }]
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

const prodiOptionSets = {
  academic_context: [
    { value: 'STEM-heavy classes', label: { en: 'STEM-heavy classes', id: 'Kelas dominan STEM' } },
    { value: 'Strong language and humanities', label: { en: 'Language and humanities', id: 'Bahasa dan humaniora' } },
    { value: 'Business and organization activities', label: { en: 'Business and organization', id: 'Bisnis dan organisasi' } },
    { value: 'Health and biology exposure', label: { en: 'Health and biology', id: 'Kesehatan dan biologi' } },
    { value: 'Art, design, and creative portfolio', label: { en: 'Art and design portfolio', id: 'Portofolio seni dan desain' } },
    { value: 'Law, debate, and public issues', label: { en: 'Law and public issues', id: 'Hukum dan isu publik' } },
    { value: 'Education and mentoring activities', label: { en: 'Education and mentoring', id: 'Pendidikan dan mentoring' } },
    { value: 'Environment and field observation', label: { en: 'Environment and fieldwork', id: 'Lingkungan dan observasi lapangan' } }
  ],
  subject_preferences: [
    { value: 'Computer Science', label: { en: 'Computer Science', id: 'Informatika' } },
    { value: 'Mathematics', label: { en: 'Mathematics', id: 'Matematika' } },
    { value: 'Physics', label: { en: 'Physics', id: 'Fisika' } },
    { value: 'Chemistry', label: { en: 'Chemistry', id: 'Kimia' } },
    { value: 'Biology', label: { en: 'Biology', id: 'Biologi' } },
    { value: 'Economics', label: { en: 'Economics', id: 'Ekonomi' } },
    { value: 'Sociology', label: { en: 'Sociology', id: 'Sosiologi' } },
    { value: 'Geography', label: { en: 'Geography', id: 'Geografi' } },
    { value: 'History', label: { en: 'History', id: 'Sejarah' } },
    { value: 'Law', label: { en: 'Law', id: 'Hukum' } },
    { value: 'Communication', label: { en: 'Communication', id: 'Komunikasi' } },
    { value: 'Design', label: { en: 'Design', id: 'Desain' } },
    { value: 'Language and literature', label: { en: 'Language and literature', id: 'Bahasa dan sastra' } },
    { value: 'Education', label: { en: 'Education', id: 'Pendidikan' } },
    { value: 'Environment', label: { en: 'Environment', id: 'Lingkungan' } }
  ],
  interest_deep_dive: [
    { value: 'Software engineering', label: { en: 'Software engineering', id: 'Rekayasa perangkat lunak' } },
    { value: 'Data and AI products', label: { en: 'Data and AI products', id: 'Produk data dan AI' } },
    { value: 'Cybersecurity and systems', label: { en: 'Cybersecurity and systems', id: 'Keamanan siber dan sistem' } },
    { value: 'Robotics and engineering design', label: { en: 'Robotics and engineering design', id: 'Robotika dan desain teknik' } },
    { value: 'Human behavior research', label: { en: 'Human behavior research', id: 'Riset perilaku manusia' } },
    { value: 'Creative visual work', label: { en: 'Creative visual work', id: 'Karya visual kreatif' } },
    { value: 'Healthcare impact', label: { en: 'Healthcare impact', id: 'Dampak kesehatan' } },
    { value: 'Finance and business analytics', label: { en: 'Finance and business analytics', id: 'Keuangan dan analitik bisnis' } },
    { value: 'Public policy and advocacy', label: { en: 'Public policy and advocacy', id: 'Kebijakan publik dan advokasi' } },
    { value: 'Teaching and curriculum', label: { en: 'Teaching and curriculum', id: 'Mengajar dan kurikulum' } },
    { value: 'Language, writing, and translation', label: { en: 'Language and translation', id: 'Bahasa dan penerjemahan' } }
  ],
  career_direction: [
    { value: 'Technology builder', label: { en: 'Technology builder', id: 'Pembuat teknologi' } },
    { value: 'Analyst or researcher', label: { en: 'Analyst or researcher', id: 'Analis atau peneliti' } },
    { value: 'Healthcare professional', label: { en: 'Healthcare professional', id: 'Profesional kesehatan' } },
    { value: 'Business leader', label: { en: 'Business leader', id: 'Pemimpin bisnis' } },
    { value: 'Creative professional', label: { en: 'Creative professional', id: 'Profesional kreatif' } },
    { value: 'Educator or mentor', label: { en: 'Educator or mentor', id: 'Pendidik atau mentor' } },
    { value: 'Legal or policy professional', label: { en: 'Legal or policy professional', id: 'Profesional hukum atau kebijakan' } },
    { value: 'Environmental field specialist', label: { en: 'Environmental field specialist', id: 'Spesialis lapangan lingkungan' } },
    { value: 'Writer, translator, or communicator', label: { en: 'Writer or translator', id: 'Penulis atau penerjemah' } }
  ],
  constraints: [
    { value: 'Prefer Jakarta only', label: { en: 'Jakarta only', id: 'Hanya Jakarta' } },
    { value: 'Prefer affordable study path', label: { en: 'Affordable path', id: 'Jalur terjangkau' } },
    { value: 'Avoid long clinical path', label: { en: 'Avoid long clinical path', id: 'Hindari klinis panjang' } },
    { value: 'Need flexible career options', label: { en: 'Flexible career options', id: 'Karier fleksibel' } },
    { value: 'Prefer fieldwork over office work', label: { en: 'Prefer fieldwork', id: 'Lebih suka kerja lapangan' } },
    { value: 'Prefer remote-friendly careers', label: { en: 'Remote-friendly careers', id: 'Karier ramah remote' } },
    { value: 'Prefer low public-speaking load', label: { en: 'Low public speaking', id: 'Sedikit public speaking' } },
    { value: 'Need clear professional license path', label: { en: 'Professional license path', id: 'Jalur lisensi profesi jelas' } }
  ],
  expected_prodi: [
    { value: 'Teknik Informatika', label: { en: 'Informatics Engineering', id: 'Teknik Informatika' } },
    { value: 'Kecerdasan Artifisial', label: { en: 'Artificial Intelligence', id: 'Kecerdasan Artifisial' } },
    { value: 'Sains Data', label: { en: 'Data Science', id: 'Sains Data' } },
    { value: 'Sistem Informasi', label: { en: 'Information Systems', id: 'Sistem Informasi' } },
    { value: 'Kedokteran', label: { en: 'Medicine', id: 'Kedokteran' } },
    { value: 'Farmasi', label: { en: 'Pharmacy', id: 'Farmasi' } },
    { value: 'Psikologi', label: { en: 'Psychology', id: 'Psikologi' } },
    { value: 'Manajemen', label: { en: 'Management', id: 'Manajemen' } },
    { value: 'Akuntansi', label: { en: 'Accounting', id: 'Akuntansi' } },
    { value: 'Hukum', label: { en: 'Law', id: 'Hukum' } },
    { value: 'Ilmu Komunikasi', label: { en: 'Communication Studies', id: 'Ilmu Komunikasi' } },
    { value: 'Desain Komunikasi Visual', label: { en: 'Visual Communication Design', id: 'Desain Komunikasi Visual' } },
    { value: 'Teknik Sipil', label: { en: 'Civil Engineering', id: 'Teknik Sipil' } },
    { value: 'Pendidikan Bahasa Inggris', label: { en: 'English Education', id: 'Pendidikan Bahasa Inggris' } },
    { value: 'Ilmu Lingkungan', label: { en: 'Environmental Science', id: 'Ilmu Lingkungan' } }
  ],
  prodi_to_avoid: [
    { value: 'Kedokteran', label: { en: 'Medicine', id: 'Kedokteran' } },
    { value: 'Farmasi', label: { en: 'Pharmacy', id: 'Farmasi' } },
    { value: 'Akuntansi', label: { en: 'Accounting', id: 'Akuntansi' } },
    { value: 'Hukum', label: { en: 'Law', id: 'Hukum' } },
    { value: 'Teknik Sipil', label: { en: 'Civil Engineering', id: 'Teknik Sipil' } },
    { value: 'Teknik Informatika', label: { en: 'Informatics Engineering', id: 'Teknik Informatika' } },
    { value: 'Manajemen', label: { en: 'Management', id: 'Manajemen' } },
    { value: 'Pendidikan Bahasa Inggris', label: { en: 'English Education', id: 'Pendidikan Bahasa Inggris' } },
    { value: 'Desain Komunikasi Visual', label: { en: 'Visual Communication Design', id: 'Desain Komunikasi Visual' } }
  ],
  free_text_goal: [
    { value: 'Build AI products', label: { en: 'Build AI products', id: 'Membangun produk AI' } },
    { value: 'Create stable career options', label: { en: 'Stable career options', id: 'Karier stabil' } },
    { value: 'Solve social problems', label: { en: 'Solve social problems', id: 'Memecahkan masalah sosial' } },
    { value: 'Keep creative work in daily role', label: { en: 'Creative daily work', id: 'Pekerjaan harian kreatif' } },
    { value: 'Work with data and research', label: { en: 'Data and research work', id: 'Bekerja dengan data dan riset' } },
    { value: 'Help people through counseling or education', label: { en: 'Help through counseling or education', id: 'Membantu lewat konseling atau pendidikan' } },
    { value: 'Build a business or manage teams', label: { en: 'Build business or manage teams', id: 'Membangun bisnis atau mengelola tim' } },
    { value: 'Create designs, media, or visual stories', label: { en: 'Designs and visual stories', id: 'Desain dan cerita visual' } },
    { value: 'Protect environment and communities', label: { en: 'Environment and communities', id: 'Lingkungan dan komunitas' } }
  ]
};

export const prodiIntakeSteps = [
  { key: 'academic_context', required: true, optionMode: 'replace', options: prodiOptionSets.academic_context, label: { en: 'Academic context', id: 'Konteks akademik' }, helper: { en: 'Choose the closest academic signal.', id: 'Pilih sinyal akademik yang paling sesuai.' } },
  { key: 'subject_preferences', required: true, optionMode: 'append', options: prodiOptionSets.subject_preferences, label: { en: 'Subject preferences', id: 'Preferensi mapel' }, helper: { en: 'Pick subjects you want more or less of in college.', id: 'Pilih mapel yang ingin lebih banyak atau lebih sedikit ditemui saat kuliah.' } },
  { key: 'interest_deep_dive', required: true, optionMode: 'replace', options: prodiOptionSets.interest_deep_dive, label: { en: 'Interest deep dive', id: 'Pendalaman minat' }, helper: { en: 'Pick the closest interest detail.', id: 'Pilih detail minat yang paling sesuai.' } },
  { key: 'career_direction', required: true, optionMode: 'replace', options: prodiOptionSets.career_direction, label: { en: 'Career direction', id: 'Arah karier' }, helper: { en: 'Pick the career direction you are considering.', id: 'Pilih arah karier yang kamu pertimbangkan.' } },
  { key: 'constraints', required: true, optionMode: 'replace', options: prodiOptionSets.constraints, label: { en: 'Constraints', id: 'Batasan' }, helper: { en: 'Pick the main constraint Apti should consider.', id: 'Pilih batasan utama yang perlu dipertimbangkan Apti.' } },
  { key: 'expected_prodi', required: false, optionMode: 'replace', options: prodiOptionSets.expected_prodi, label: { en: 'Expected prodi', id: 'Prodi yang diharapkan' }, helper: { en: 'Optional. Pick one program you already expect or want to compare.', id: 'Opsional. Pilih satu prodi yang sudah kamu harapkan atau ingin bandingkan.' } },
  { key: 'prodi_to_avoid', required: false, optionMode: 'append', options: prodiOptionSets.prodi_to_avoid, label: { en: 'Prodi to avoid', id: 'Prodi yang dihindari' }, helper: { en: 'Optional. Pick programs Apti should avoid unless strongly justified.', id: 'Opsional. Pilih prodi yang sebaiknya dihindari kecuali sangat kuat alasannya.' } },
  { key: 'free_text_goal', required: false, optionMode: 'replace', options: prodiOptionSets.free_text_goal, label: { en: 'Goal', id: 'Tujuan' }, helper: { en: 'Optional. Pick the closest goal.', id: 'Opsional. Pilih tujuan terdekat.' } }
];

export const commonKelas10Subjects = [
  ['religion', 'Pendidikan Agama'],
  ['civics', 'PPKn'],
  ['indonesian', 'Bahasa Indonesia'],
  ['english', 'Bahasa Inggris'],
  ['general_math', 'Matematika Umum'],
  ['pjok', 'PJOK'],
  ['arts', 'Seni']
];

export function subjectsForGrade(trackKey, grade, selectedElectives = []) {
  if (grade === 10) return commonKelas10Subjects;
  const track = trackConfig[trackKey];
  const baseSubjects = [...(track?.requiredSubjects || []), ...(track?.optionalSubjects || [])];
  if (trackKey !== 'Merdeka') return baseSubjects;
  const electives = (track?.electiveSubjects || []).filter(([key]) => selectedElectives.includes(key));
  return [...baseSubjects, ...electives];
}

export function buildInitialScores(trackKey) {
  const track = trackConfig[trackKey];
  const subjectKeys = [
    ...(track?.requiredSubjects || []).map(([key]) => key),
    ...(track?.optionalSubjects || []).map(([key]) => key)
  ];

  return Object.fromEntries(subjectKeys.map((key) => [key, '']));
}

export function buildInitialRaporScores(trackKey, selectedElectives = []) {
  const entries = [];
  for (const grade of [10, 11, 12]) {
    for (const semester of grade === 10 ? [1, 2] : grade === 11 ? [3, 4] : [5, 6]) {
      for (const [subject] of subjectsForGrade(trackKey, grade, selectedElectives)) entries.push([`s${semester}_${subject}`, '']);
    }
  }
  return Object.fromEntries(entries);
}

export function buildRaporPayload(raporScores, trackKey, selectedElectives = []) {
  const semesterToBucket = { 1: 'kelas_10', 2: 'kelas_10', 3: 'kelas_11', 4: 'kelas_11', 5: 'kelas_12', 6: 'kelas_12' };
  const payload = { kelas_10: [], kelas_11: [], kelas_12: [], sma_track: trackKey, curriculum_type: trackConfig[trackKey]?.curriculumType, merdeka_electives: selectedElectives };
  Object.entries(raporScores).forEach(([key, value]) => {
    const match = key.match(/^s([1-6])_(.+)$/);
    const parsed = Number(value);
    if (!match || !Number.isFinite(parsed) || parsed < 0 || parsed > 100) return;
    payload[semesterToBucket[match[1]]].push({ semester: Number(match[1]), subject: match[2], score: parsed });
  });
  return payload;
}
