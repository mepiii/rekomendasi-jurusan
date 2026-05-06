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



const makeOption = (id, labelId, labelEn, tags = [], clusterTags = [], conflictTags = [], scoringWeight = 1) => ({
  id,
  value: labelId,
  label: { id: labelId, en: labelEn },
  label_id: labelId,
  label_en: labelEn,
  tags,
  cluster_tags: clusterTags,
  conflict_tags: conflictTags,
  scoring_weight: scoringWeight
});

export const surveyModeOptions = [
  makeOption('mode_target', 'Aku sudah punya target prodi', 'I already have target majors', ['target_checker'], ['target'], [], 1),
  makeOption('mode_compare', 'Aku ragu antara beberapa prodi', 'I am comparing several majors', ['compare_mode'], ['target'], [], 1),
  makeOption('mode_cluster', 'Aku cuma tahu bidang/fakultas', 'I only know the field or faculty', ['cluster_exploration'], ['cluster'], [], 1),
  makeOption('mode_unknown', 'Aku belum tahu sama sekali', 'I have no idea yet', ['guided_exploration'], ['exploration'], [], 1),
  makeOption('mode_zero', 'Aku ingin rekomendasi dari nol', 'I want Apti to recommend from zero', ['from_zero'], ['exploration'], [], 1)
];

export const clusterOptions = [
  ['komputer_digital', 'Komputer & Digital', 'Computer & Digital'],
  ['teknik_infrastruktur', 'Teknik & Infrastruktur', 'Engineering & Infrastructure'],
  ['kesehatan_kedokteran', 'Kesehatan & Kedokteran', 'Health & Medicine'],
  ['farmasi_bioteknologi', 'Farmasi & Bioteknologi', 'Pharmacy & Biotechnology'],
  ['psikologi_konseling', 'Psikologi & Konseling', 'Psychology & Counseling'],
  ['pendidikan_keguruan', 'Pendidikan & Keguruan', 'Education & Teaching'],
  ['ekonomi_bisnis', 'Ekonomi, Bisnis & Manajemen', 'Economics, Business & Management'],
  ['hukum_kebijakan', 'Hukum & Kebijakan Publik', 'Law & Public Policy'],
  ['komunikasi_media', 'Komunikasi, Media & Jurnalistik', 'Communication, Media & Journalism'],
  ['seni_desain', 'Seni, Desain & Industri Kreatif', 'Art, Design & Creative Industry'],
  ['bahasa_humaniora', 'Bahasa, Sastra & Humaniora', 'Language, Literature & Humanities'],
  ['mipa_sains', 'MIPA & Riset Sains', 'Science & Research'],
  ['lingkungan_kebumian', 'Lingkungan, Geografi & Kebumian', 'Environment, Geography & Earth Science'],
  ['pangan_agribisnis', 'Pangan, Pertanian & Agribisnis', 'Food, Agriculture & Agribusiness'],
  ['pariwisata_event', 'Pariwisata, Perhotelan & Event', 'Tourism, Hospitality & Event'],
  ['logistik_transportasi', 'Transportasi, Logistik & Supply Chain', 'Transport, Logistics & Supply Chain'],
  ['olahraga', 'Olahraga & Keolahragaan', 'Sports Science'],
  ['administrasi_publik', 'Administrasi, Pemerintahan & Layanan Publik', 'Public Administration & Services']
].map(([id, labelId, labelEn]) => makeOption(`cluster_${id}`, labelId, labelEn, [id], [id]));

const tag = (name) => name.toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
const optionFrom = (labelId, labelEn, clusters, conflicts = []) => makeOption(tag(labelEn), labelId, labelEn, [tag(labelEn)], clusters, conflicts, 1);

export const explorationOptionSets = {
  academic_strength: ['Kuat di matematika|Strong in mathematics|mipa_sains,komputer_digital', 'Kuat di logika|Strong in logic|komputer_digital,mipa_sains', 'Kuat di sains|Strong in science|mipa_sains,kesehatan_kedokteran', 'Kuat di bahasa|Strong in language|bahasa_humaniora,komunikasi_media', 'Kuat di sosial|Strong in social studies|sosial_politik,hukum_kebijakan', 'Kuat di ekonomi|Strong in economics|ekonomi_bisnis', 'Kuat di seni/desain|Strong in art/design|seni_desain', 'Kuat di teknologi|Strong in technology|komputer_digital', 'Kuat di komunikasi|Strong in communication|komunikasi_media', 'Kuat di riset|Strong in research|mipa_sains', 'Kuat di kerja lapangan|Strong in fieldwork|lingkungan_kebumian', 'Kuat di data dan angka|Strong in data and numbers|komputer_digital,akuntansi_keuangan'].map((s) => { const [id,en,c]=s.split('|'); return optionFrom(id,en,c.split(',')); }),
  subject_likes: ['Matematika Umum|General Math|mipa_sains', 'Matematika Lanjut|Advanced Math|mipa_sains,komputer_digital', 'Informatika|Informatics|komputer_digital', 'Fisika|Physics|teknik_infrastruktur,mipa_sains', 'Kimia|Chemistry|farmasi_bioteknologi,teknik_infrastruktur', 'Biologi|Biology|kesehatan_kedokteran,farmasi_bioteknologi', 'Ekonomi|Economics|ekonomi_bisnis', 'Sosiologi|Sociology|sosial_politik', 'Geografi|Geography|lingkungan_kebumian', 'Sejarah|History|bahasa_humaniora', 'Bahasa Inggris|English|bahasa_humaniora', 'Seni|Arts|seni_desain', 'Akuntansi|Accounting|akuntansi_keuangan', 'Psikologi|Psychology|psikologi_konseling', 'Kesehatan|Health|kesehatan_kedokteran', 'Pangan|Food|pangan_agribisnis'].map((s) => { const [id,en,c]=s.split('|'); return optionFrom(id,en,c.split(',')); }),
  avoid_signals: ['Matematika berat|Heavy mathematics|mipa_sains,komputer_digital|math_heavy', 'Coding|Coding|komputer_digital|coding', 'Biologi/lab|Biology/lab|kesehatan_kedokteran,farmasi_bioteknologi|lab', 'Banyak membaca teori|Heavy theory reading|hukum_kebijakan,bahasa_humaniora|reading_heavy', 'Banyak presentasi|Many presentations|komunikasi_media,pendidikan_keguruan|public_speaking', 'Banyak debat|Frequent debate|hukum_kebijakan|debate', 'Banyak kerja lapangan|Frequent fieldwork|lingkungan_kebumian,teknik_infrastruktur|fieldwork', 'Banyak tugas portofolio|Portfolio-heavy tasks|seni_desain|portfolio', 'Pendidikan profesi lanjutan|Long professional education|kesehatan_kedokteran|long_education'].map((s) => { const [id,en,c,conf]=s.split('|'); return optionFrom(id,en,c.split(','), [conf]); }),
  activities: ['Membuat aplikasi|Building apps|komputer_digital', 'Mengolah data|Analyzing data|komputer_digital,mipa_sains', 'Membuat desain|Creating designs|seni_desain', 'Menulis|Writing|bahasa_humaniora,komunikasi_media', 'Mengajar teman|Teaching friends|pendidikan_keguruan', 'Berdebat|Debating|hukum_kebijakan', 'Eksperimen laboratorium|Lab experiments|farmasi_bioteknologi,kesehatan_kedokteran', 'Observasi lapangan|Field observation|lingkungan_kebumian', 'Membantu orang|Helping people|psikologi_konseling,kesehatan_kedokteran', 'Memimpin tim|Leading teams|ekonomi_bisnis'].map((s) => { const [id,en,c]=s.split('|'); return optionFrom(id,en,c.split(',')); }),
  career_goals: ['Gaji tinggi|High salary|komputer_digital,ekonomi_bisnis', 'Karier stabil|Stable career|administrasi_publik,kesehatan_kedokteran', 'Bisa kerja remote|Remote-friendly work|komputer_digital,komunikasi_media', 'Bisa membantu banyak orang|Help many people|kesehatan_kedokteran,pendidikan_keguruan', 'Bisa membangun bisnis sendiri|Build my own business|ekonomi_bisnis', 'Bisa menjadi profesional berlisensi|Licensed professional path|hukum_kebijakan,kesehatan_kedokteran', 'Tidak mudah tergantikan AI|Resistant to AI change|kesehatan_kedokteran,psikologi_konseling', 'Bisa lintas bidang|Cross-disciplinary career|komputer_digital,ekonomi_bisnis'].map((s) => { const [id,en,c]=s.split('|'); return optionFrom(id,en,c.split(',')); })
};

export const targetSpecificOptionSets = Object.fromEntries([
  'Teknik Informatika', 'Ilmu Komputer', 'Sistem Informasi', 'Kecerdasan Artifisial', 'Sains Data', 'Teknik Sipil', 'Teknik Mesin', 'Teknik Elektro', 'Teknik Industri', 'Teknik Kimia', 'Teknik Lingkungan', 'Arsitektur', 'Kedokteran', 'Kedokteran Gigi', 'Keperawatan', 'Farmasi', 'Gizi', 'Kesehatan Masyarakat', 'Psikologi', 'Pendidikan Guru SD', 'Pendidikan Bahasa Inggris', 'Akuntansi', 'Manajemen', 'Ekonomi', 'Bisnis Digital', 'Hukum', 'Hubungan Internasional', 'Administrasi Publik', 'Sosiologi', 'Ilmu Komunikasi', 'Jurnalistik', 'Desain Komunikasi Visual', 'Film dan Televisi', 'Sastra Inggris', 'Statistika', 'Matematika', 'Bioteknologi', 'Teknologi Pangan', 'Agribisnis', 'Agroteknologi', 'Peternakan', 'Ilmu Kelautan', 'Ilmu Lingkungan', 'Geografi', 'Geologi', 'Pariwisata', 'Perhotelan', 'Manajemen Logistik', 'Ilmu Keolahragaan'
].map((major) => [major, [
  makeOption(`${tag(major)}_fit_1`, `Saya tertarik memahami inti ${major}`, `I want to understand the core of ${major}`, ['target_fit', tag(major)], [tag(major)], [], 1),
  makeOption(`${tag(major)}_fit_2`, 'Saya siap memperkuat skill dasar', 'I am ready to strengthen fundamentals', ['readiness', 'skill_gap'], [tag(major)], [], 1),
  makeOption(`${tag(major)}_fit_3`, 'Saya ingin melihat risiko dan alternatifnya', 'I want to see risks and alternatives', ['conflict_check', 'alternative'], [tag(major)], [], 1),
  makeOption(`${tag(major)}_fit_4`, 'Saya ingin tahu jalur kariernya', 'I want to know the career path', ['career_goal'], [tag(major)], [], 1),
  makeOption(`${tag(major)}_fit_5`, 'Saya siap dibandingkan dengan prodi mirip', 'I am ready to compare similar majors', ['compare_mode'], [tag(major)], [], 1),
  makeOption(`${tag(major)}_risk_1`, 'Saya khawatir beban kuliahnya terlalu berat', 'I worry the workload may be too heavy', ['risk'], [tag(major)], ['workload'], 0.8),
  makeOption(`${tag(major)}_risk_2`, 'Saya belum yakin cocok dengan gaya belajarnya', 'I am unsure about the learning style fit', ['risk'], [tag(major)], ['learning_style'], 0.8),
  makeOption(`${tag(major)}_roadmap_1`, 'Saya ingin roadmap belajar awal', 'I want a beginner learning roadmap', ['roadmap', 'skill_gap'], [tag(major)], [], 1)
]]));

export const expandedMajorOptions = [
  'Teknik Informatika','Ilmu Komputer','Sistem Informasi','Kecerdasan Artifisial','Sains Data','Teknik Sipil','Teknik Mesin','Teknik Elektro','Teknik Industri','Teknik Kimia','Teknik Lingkungan','Arsitektur','Perencanaan Wilayah dan Kota','Kedokteran','Kedokteran Gigi','Kedokteran Hewan','Keperawatan','Kebidanan','Farmasi','Gizi','Kesehatan Masyarakat','Psikologi','Pendidikan Guru SD','Pendidikan Bahasa Inggris','Pendidikan Matematika','Bimbingan Konseling','Akuntansi','Manajemen','Ekonomi','Bisnis Digital','Hukum','Hubungan Internasional','Administrasi Publik','Sosiologi','Ilmu Politik','Ilmu Komunikasi','Jurnalistik','Desain Komunikasi Visual','Film dan Televisi','Sastra Inggris','Sastra Indonesia','Statistika','Matematika','Biologi','Kimia','Fisika','Bioteknologi','Teknologi Pangan','Agribisnis','Agroteknologi','Peternakan','Ilmu Kelautan','Perikanan','Ilmu Lingkungan','Geografi','Geologi','Pariwisata','Perhotelan','Manajemen Logistik','Transportasi','Ilmu Keolahragaan','Administrasi Bisnis','Administrasi Negara','Perpajakan','Keuangan','Marketing','Teknik Arsitektur','Desain Interior','Desain Produk','Animasi','Fotografi','Antropologi','Filsafat','Sejarah','Bahasa Jepang','Bahasa Mandarin','Pendidikan Biologi','Pendidikan Fisika','Pendidikan Kimia','Pendidikan Ekonomi','Pendidikan Sejarah','Teknik Pertambangan','Teknik Geologi','Teknik Perkapalan','Teknik Material','Teknik Biomedis','Rekayasa Perangkat Lunak','Sistem Komputer','Teknologi Informasi','Data Analytics','Aktuaria','Manajemen Rekayasa','Ilmu Pemerintahan','Kesejahteraan Sosial','Kriminologi','Hubungan Masyarakat','Penyiaran','Manajemen Event','Manajemen Perhotelan','Tata Boga','Teknologi Hasil Pertanian','Kehutanan','Ilmu Tanah','Proteksi Tanaman','Budidaya Perairan','Oseanografi','Meteorologi','Keselamatan Kerja','Rekam Medis','Teknologi Laboratorium Medis'
].map((name) => makeOption(`major_${tag(name)}`, name, name, [tag(name)], [tag(name)]));

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
  expected_prodi: expandedMajorOptions,
  prodi_to_avoid: expandedMajorOptions,
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
  { key: 'academic_context', required: true, optionMode: 'append', maxSelections: 8, options: explorationOptionSets.academic_strength, label: { en: 'Academic strengths', id: 'Kekuatan akademik' }, helper: { en: 'Pick signals that describe you. Multiple choices are normalized.', id: 'Pilih sinyal yang menggambarkan kamu. Banyak pilihan akan dinormalisasi.' } },
  { key: 'subject_preferences', required: true, optionMode: 'append', maxSelections: 10, options: explorationOptionSets.subject_likes, label: { en: 'Liked subjects', id: 'Mapel yang disukai' }, helper: { en: 'Pick subjects you enjoy most.', id: 'Pilih mapel yang paling kamu sukai.' } },
  { key: 'avoid_signals', required: false, optionMode: 'append', maxSelections: 8, options: explorationOptionSets.avoid_signals, label: { en: 'Things to avoid', id: 'Hal yang ingin dihindari' }, helper: { en: 'Pick academic or work patterns you want Apti to penalize.', id: 'Pilih pola akademik atau kerja yang perlu diberi penalti.' } },
  { key: 'interest_deep_dive', required: true, optionMode: 'append', maxSelections: 8, options: prodiOptionSets.interest_deep_dive, label: { en: 'General interests', id: 'Minat umum' }, helper: { en: 'Pick the fields that feel interesting.', id: 'Pilih bidang yang terasa menarik.' } },
  { key: 'activities', required: true, optionMode: 'append', maxSelections: 8, options: explorationOptionSets.activities, label: { en: 'Activities you enjoy', id: 'Aktivitas yang disukai' }, helper: { en: 'Pick activities you would not mind doing often.', id: 'Pilih aktivitas yang tidak keberatan kamu lakukan sering.' } },
  { key: 'career_direction', required: true, optionMode: 'append', maxSelections: 8, options: prodiOptionSets.career_direction, label: { en: 'Career direction', id: 'Arah karier' }, helper: { en: 'Pick career directions you are considering.', id: 'Pilih arah karier yang kamu pertimbangkan.' } },
  { key: 'career_goals', required: true, optionMode: 'append', maxSelections: 8, options: explorationOptionSets.career_goals, label: { en: 'Career goals', id: 'Tujuan karier' }, helper: { en: 'Pick outcomes that matter most.', id: 'Pilih hasil yang paling penting.' } },
  { key: 'constraints', required: true, optionMode: 'append', maxSelections: 8, options: prodiOptionSets.constraints, label: { en: 'Constraints', id: 'Batasan' }, helper: { en: 'Pick limits or preferences Apti should consider.', id: 'Pilih batasan atau preferensi yang perlu dipertimbangkan Apti.' } },
  { key: 'target_clusters', required: false, optionMode: 'append', maxSelections: 4, showForModes: ['mode_cluster'], options: clusterOptions, label: { en: 'Known fields or faculties', id: 'Bidang atau fakultas yang diketahui' }, helper: { en: 'Optional. Pick broad clusters you already know.', id: 'Opsional. Pilih bidang luas yang sudah kamu tahu.' } },
  { key: 'expected_prodi', required: false, optionMode: 'append', maxSelections: 4, showForModes: ['mode_target', 'mode_compare'], options: prodiOptionSets.expected_prodi, label: { en: 'Target majors', id: 'Target jurusan/prodi' }, helper: { en: 'Optional. Pick up to 4 targets for checking or comparison.', id: 'Opsional. Pilih maksimal 4 target untuk dicek atau dibandingkan.' } },
  { key: 'target_specific', required: false, optionMode: 'append', maxSelections: 8, showForModes: ['mode_target', 'mode_compare'], adaptiveTarget: true, options: [], label: { en: 'Target deep dive', id: 'Pendalaman target' }, helper: { en: 'Shown only when target majors are selected.', id: 'Muncul hanya saat target prodi dipilih.' } },
  { key: 'prodi_to_avoid', required: false, optionMode: 'append', maxSelections: 6, options: prodiOptionSets.prodi_to_avoid, label: { en: 'Majors to avoid', id: 'Jurusan yang dihindari' }, helper: { en: 'Optional. These receive a penalty, not automatic deletion.', id: 'Opsional. Ini diberi penalti, bukan dihapus otomatis.' } },
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
