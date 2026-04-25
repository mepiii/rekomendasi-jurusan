// Purpose: Provide localizable copy, locale persistence, and shared label dictionaries for Apti UI.
// Callers: App shell, recommendation journey, results surface.
// Deps: Browser localStorage when available.
// API: loadLocale(), saveLocale(), copy, localeOptions.
// Side effects: Persists selected locale in localStorage.
export const LOCALE_KEY = 'apti-locale';
export const defaultLocale = 'en';
export const localeOptions = ['en', 'id'];

export function loadLocale() {
  const stored = window.localStorage.getItem(LOCALE_KEY);
  return localeOptions.includes(stored) ? stored : defaultLocale;
}

export function saveLocale(locale) {
  const nextLocale = localeOptions.includes(locale) ? locale : defaultLocale;
  window.localStorage.setItem(LOCALE_KEY, nextLocale);
  return nextLocale;
}

export const copy = {
  en: {
    appName: 'Apti',
    themeLight: 'Light mode',
    themeDark: 'Dark mode',
    languageLabel: 'Language',
    restartIntro: 'Restart intro',
    introFallbackTitle: 'Welcome back, there',
    journeyKicker: 'Apti advisory workspace',
    journeyTitle: 'Discover a study path that truly fits you.',
    journeyHelper: 'Share your latest academic signals, interests, and learning preferences to get a sharper shortlist of majors.',
    steps: ['Track', 'Profile', 'Academic', 'Subjects', 'Interests', 'Career', 'Constraints', 'Expected', 'Avoid', 'Goal', 'Review'],
    continue: 'Continue',
    back: 'Back',
    analyze: 'Analyze profile',
    analyzing: 'Analyzing...',
    profileReview: 'Profile review',
    decisionSupport: 'These results are decision support, not a final answer. Confirm them with a counselor, mentor, or trusted teacher.',
    track: 'Track',
    subjects: 'Subjects',
    interests: 'Interests',
    preferences: 'Preferences',
    selected: 'selected',
    topRecommendations: 'Your best-fit study directions',
    resultIntro: 'A calmer readout of your academic profile, strongest signals, and recommended majors worth reviewing next.',
    strongestSubject: 'Strongest subject',
    strongestGroup: 'Strongest group',
    averageScore: 'Average score',
    confidence: 'Confidence',
    reflection: 'Reflection',
    reflectionPrompt: 'Does this direction match what you want next?',
    reflectionHelper: 'Share whether Apti feels aligned so future recommendations can become steadier and more useful.',
    yesMatch: 'Yes, it matches',
    notYet: 'Not yet',
    actualMajor: 'Select your actual major (optional)',
    rating: 'Rating 1-5',
    notes: 'Additional notes...',
    sendFeedback: 'Send feedback',
    saving: 'Saving...',
    tryDifferentInputs: 'Try different inputs',
    feedbackSaved: 'Feedback saved. Thank you.',
    feedbackFailed: 'Failed to save feedback. Please try again.',
    disclaimer: 'These results are decision support, not a final verdict. Review them with a counselor, teacher, parent, or trusted mentor.',
    topRecommendation: 'Top recommendation',
    whyThis: 'Why this?',
    waitingExplainability: 'Waiting for explainability data...',
    strengths: 'Strength signals',
    tradeoffs: 'Tradeoffs to review',
    careerPaths: 'Related career paths',
    alternateMajors: 'Alternative majors',
    goals: {
      'find-fit': 'Find a grounded starting point with recommendations shaped around your strongest signals.',
      'compare-majors': 'Compare majors side by side with refreshed recommendations and clearer tradeoffs.',
      'understand-strengths': 'Start with your strengths, then turn them into a short list of promising majors.'
    },
    inputsError: 'Please review the required fields before continuing.',
    busyError: 'System is busy right now. Please try again in a moment.',
    invalidError: 'Invalid input. Please review the profile you entered.',
    systemError: 'A system error occurred.',
    genericError: 'Something went wrong. Please try again shortly.'
  },
  id: {
    appName: 'Apti',
    themeLight: 'Mode terang',
    themeDark: 'Mode gelap',
    languageLabel: 'Bahasa',
    restartIntro: 'Ulang intro',
    introFallbackTitle: 'Selamat datang kembali',
    journeyKicker: 'Ruang arahan Apti',
    journeyTitle: 'Temukan jurusan yang paling sesuai dengan dirimu.',
    journeyHelper: 'Bagikan sinyal akademik, minat, dan preferensi belajarmu untuk mendapat daftar jurusan yang lebih tepat.',
    steps: ['Jalur', 'Profil', 'Akademik', 'Mapel', 'Minat', 'Karier', 'Batasan', 'Target', 'Hindari', 'Tujuan', 'Tinjau'],
    continue: 'Lanjut',
    back: 'Kembali',
    analyze: 'Analisis profil',
    analyzing: 'Menganalisis...',
    profileReview: 'Ringkasan profil',
    decisionSupport: 'Hasil ini membantu pengambilan keputusan, bukan jawaban final. Konfirmasikan dengan guru BK, mentor, atau guru yang kamu percaya.',
    track: 'Jalur',
    subjects: 'Mata pelajaran',
    interests: 'Minat',
    preferences: 'Preferensi',
    selected: 'dipilih',
    topRecommendations: 'Arah jurusan paling cocok untukmu',
    resultIntro: 'Ringkasan tenang tentang profil akademikmu, sinyal terkuatmu, dan jurusan yang layak kamu pertimbangkan.',
    strongestSubject: 'Mata pelajaran terkuat',
    strongestGroup: 'Kelompok terkuat',
    averageScore: 'Rata-rata nilai',
    confidence: 'Kepercayaan',
    reflection: 'Refleksi',
    reflectionPrompt: 'Apakah arah ini sesuai dengan yang kamu inginkan?',
    reflectionHelper: 'Bagikan apakah Apti terasa cocok agar rekomendasi berikutnya semakin stabil dan berguna.',
    yesMatch: 'Ya, cocok',
    notYet: 'Belum',
    actualMajor: 'Pilih jurusan sebenarnya (opsional)',
    rating: 'Nilai 1-5',
    notes: 'Catatan tambahan...',
    sendFeedback: 'Kirim masukan',
    saving: 'Menyimpan...',
    tryDifferentInputs: 'Coba input lain',
    feedbackSaved: 'Masukan tersimpan. Terima kasih.',
    feedbackFailed: 'Masukan gagal disimpan. Coba lagi.',
    disclaimer: 'Hasil ini membantu pengambilan keputusan, bukan vonis akhir. Tinjau bersama guru BK, guru, orang tua, atau mentor tepercaya.',
    topRecommendation: 'Rekomendasi utama',
    whyThis: 'Kenapa ini?',
    waitingExplainability: 'Menunggu data penjelasan...',
    strengths: 'Sinyal kekuatan',
    tradeoffs: 'Hal yang perlu ditinjau',
    careerPaths: 'Arah karier terkait',
    alternateMajors: 'Jurusan alternatif',
    goals: {
      'find-fit': 'Temukan titik awal yang lebih tepat berdasarkan sinyal terkuatmu.',
      'compare-majors': 'Bandingkan beberapa jurusan dengan rekomendasi yang lebih segar dan tradeoff yang lebih jelas.',
      'understand-strengths': 'Mulai dari kekuatanmu, lalu ubah menjadi daftar jurusan yang menjanjikan.'
    },
    inputsError: 'Periksa lagi field wajib sebelum lanjut.',
    busyError: 'Sistem sedang sibuk. Coba lagi sebentar.',
    invalidError: 'Input tidak valid. Periksa lagi profil yang kamu isi.',
    systemError: 'Terjadi kesalahan sistem.',
    genericError: 'Terjadi kendala. Coba lagi sebentar.'
  }
};
