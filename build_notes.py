# -*- coding: utf-8 -*-
"""Rebuild app/data/notes.json with rich, multi-page notes for all 4 rounds.
All four rounds are grounded in extracted source text. Round 4 is now backed by
a Rumi (romanised) translation of Kitab Penawar Bagi Hati supplied as reference.
"""
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

OUT = "app/data/notes.json"

# Load the existing file (Round 1 already written richly) and keep Round 1 as-is.
with open(OUT, encoding="utf-8") as f:
    data = json.load(f)

round1 = data["books"][0]  # preserve the detailed Round 1 we authored

round2 = {
 "round": 2, "topic": "Fiqh Keluarga",
 "title": "Al-Fiqh Al-Manhaji, Jilid 4 (Mazhab Syafi'i)",
 "scope": "Ahwal Asy-Syakhshiyyah (Hukum-hukum Keluarga)",
 "mode": "Round 2 - dijawab secara individu oleh seorang peserta.",
 "verified": True,
 "sections": [
  {"heading": "Pengenalan Kitab & Skop", "points": [
   "Al-Fiqh Al-Manhaji ialah kitab fiqh mazhab Imam al-Syafi'i, dikarang oleh Dr. Mustafa al-Khin, Dr. Mustafa al-Bugha dan Syeikh Ali al-Syarbaji.",
   "Jilid 4 khusus membincangkan 'Ahwal Asy-Syakhshiyyah' - hukum keluarga dan segala akibat material serta moralnya.",
   "Kandungan utama: (1) Nikah, (2) Talak & yang berkaitan, (3) Nafkah, (4) Hadhanah, (5) Radha'ah, (6) Nasab, (7) Laqith.",
   "Bagi Round 2, kuasai definisi, rukun, syarat, pembahagian dan hukum. Soalan sering menguji perbezaan istilah (talak sunni vs bid'i; ila' vs zihar vs li'an)."]},
  {"heading": "Nikah - Definisi, Hukum & Hikmah", "points": [
   "Bahasa: penggabungan/penyatuan. Syarak: akad yang menghalalkan hubungan suami isteri dengan cara yang disyariatkan.",
   "Dalil pensyariatan: al-Quran, al-Sunnah dan ijmak ulama.",
   "Hukum nikah berubah ikut keadaan: sunat (asal), wajib (bimbang zina & mampu), makruh (tak mampu nafkah), haram (berniat menyakiti).",
   "Yang belum mampu berkahwin: dianjurkan berpuasa untuk menahan nafsu dan menjaga kesucian.",
   "Hikmah: memelihara maruah & akhlak, meneruskan keturunan soleh, ketenangan jiwa (sakinah), mengeratkan silaturahim & kerjasama."]},
  {"heading": "Nikah - Wanita Yang Haram Dinikahi", "points": [
   "Keharaman KEKAL: (1) nasab/keturunan, (2) mushaharah/persemendaan, (3) radha'ah/penyusuan.",
   "Haram kerana nasab: ibu (ke atas), anak perempuan (ke bawah), saudara perempuan, emak/bapa saudara, anak saudara perempuan. Sepupu TIDAK haram.",
   "Haram kerana mushaharah: ibu mertua, anak tiri (dalam jagaan), isteri anak (menantu), isteri bapa.",
   "Haram kerana radha'ah: sama seperti nasab - 'menyusu mengharamkan apa yang diharamkan oleh keturunan' (hadis).",
   "Keharaman SEMENTARA: himpun dua saudara perempuan serentak, himpun wanita dgn emak/anak saudaranya, kahwini wanita beriddah, atau isteri yang sudah cukup empat."]},
  {"heading": "Nikah - Poligami", "points": [
   "Had maksimum EMPAT isteri serentak. Tidak boleh menambah isteri kelima selagi ada empat.",
   "Hukum asal poligami: mubah (harus).",
   "Menjadi HARAM apabila lelaki yakin/kuat sangkaan tidak mampu berlaku adil.",
   "Keadilan WAJIB (praktikal): nafkah, tempat tinggal, giliran bermalam, layanan yang baik.",
   "Keadilan cinta hati sepenuhnya TIDAK dituntut (di luar kuasa manusia), tetapi kecenderungan hati tak boleh membawa kezaliman."]},
  {"heading": "Nikah - Rukun & Syarat Akad", "points": [
   "LIMA rukun: (1) Sighah (ijab & kabul), (2) Isteri, (3) Suami, (4) Wali, (5) Dua saksi.",
   "Sighah = ijab (wali) + kabul (suami). Walimah dan mahar BUKAN rukun akad.",
   "Ijab & kabul mesti bersambung tanpa sela panjang.",
   "Akad digantung pada syarat masa hadapan ('sah bila lulus peperiksaan') = TIDAK SAH; nikah mesti mutlak.",
   "Nikah dibataskan tempoh (mut'ah, 'selama sebulan') = TIDAK SAH.",
   "Saksi minimum: dua lelaki adil. Pertunangan (khitbah) tidak menghalalkan khalwat - masih ajnabi sehingga akad."]},
  {"heading": "Talak - Definisi & Pembahagian", "points": [
   "Talak: melepaskan ikatan pernikahan dengan lafaz talak atau seumpamanya.",
   "Lafaz: (1) Sarih (jelas) - jatuh tanpa niat; (2) Kinayah (sindiran) - jatuh jika disertai niat.",
   "Talak SUNNI: ketika isteri suci & belum disetubuhi dalam tempoh suci itu.",
   "Talak BID'I: ketika haid/nifas, atau dalam suci yang telah disetubuhi - tercela.",
   "Bilangan: satu & dua = raj'i (boleh rujuk); tiga = ba'in kubra (tak boleh rujuk kecuali wanita kahwin & cerai sah dgn lelaki lain)."]},
  {"heading": "Talak - Rujuk, Khulu' & Yang Menyerupai Talak", "points": [
   "Rujuk (raj'i): selagi iddah belum tamat, TANPA akad/mahar baharu (lafaz: 'Aku rujuk engkau').",
   "Khulu': perpisahan atas permintaan isteri dengan tebusan (iwad). Kembali memerlukan AKAD & MAHAR baharu.",
   "Ila': sumpah suami tidak menyetubuhi isteri - membawa kesan hukum jika berterusan.",
   "Zihar: menyamakan isteri dengan wanita mahram ('engkau seperti belakang ibuku') - haram, wajib kaffarah sebelum menyentuh isteri.",
   "Li'an: sumpah bersabung berkaitan tuduhan zina atau penafian nasab apabila tiada saksi.",
   "Wanita ditalak SEBELUM dukhul TIDAK mempunyai iddah."]},
  {"heading": "Nafkah", "points": [
   "Nafkah asas isteri: makanan, pakaian, tempat tinggal - secara MAKRUF dan menurut kemampuan.",
   "Nafkah anak: pada asasnya tanggungjawab AYAH (keperluan hidup & pendidikan).",
   "Anak berkemampuan WAJIB menafkahi ibu bapa yang miskin & memerlukan.",
   "Nafkah kerabat: dinilai ikut keperluan penerima & kemampuan pemberi.",
   "Upah penyusuan selepas cerai termasuk nafkah anak (ditanggung ayah)."]},
  {"heading": "Hadhanah (Pengasuhan Anak)", "points": [
   "Hadhanah: pemeliharaan & pengasuhan anak yang belum mampu urus diri.",
   "Ibu paling berhak pada peringkat awal - lebih belas kasihan & sesuai menjaga anak kecil.",
   "Sebab ibu didahulukan: kelembutan, kesabaran, kesesuaian fitrah mengasuh.",
   "Prinsip TERTINGGI: maslahat & keselamatan anak - bukan semata hak penjaga.",
   "Syarat penjaga: berakal, baligh, amanah, mampu mendidik, Islam (keadaan tertentu). Jika ibu gugur syarat, hak berpindah ikut susunan."]},
  {"heading": "Radha'ah, Nasab & Laqith", "points": [
   "Radha'ah (penyusuan): mewujudkan mahram & mengharamkan nikah sebagaimana nasab.",
   "Radha'ah TIDAK mewujudkan hak saling mewarisi (pusaka) - hanya larangan nikah & mahram.",
   "Nasab: hubungan darah. Kaedah: 'Anak bagi pemilik hamparan/ranjang' (al-walad lil-firasy) - anak dinisbah kepada suami dalam nikah sah.",
   "Kesan nasab sah: mahram, nafkah, perwalian (wali), pusaka.",
   "Laqith (anak temuan): bayi tanpa penjaga diketahui. Mengambilnya = fardu kifayah; jaga nyawa, kehormatan & hartanya (jika ada)."]},
  {"heading": "Ringkasan Cepat Round 2", "points": [
   "Nikah: akad menghalalkan; 5 rukun (sighah, isteri, suami, wali, 2 saksi); had 4; adil (nafkah/tempat/giliran/layanan).",
   "Talak: sarih vs kinayah; sunni vs bid'i; raj'i (rujuk tanpa akad) vs khulu' (perlu akad+mahar baharu).",
   "Ila' (sumpah tak setubuh); Zihar (samakan isteri dgn mahram); Li'an (sumpah tuduh zina/nafi nasab).",
   "Nafkah (ayah tanggung anak); Hadhanah (ibu utama, maslahat anak); Radha'ah (mahram bukan pusaka); Nasab (anak bagi pemilik ranjang); Laqith (jaga nyawa & harta)."]},
 ]
}

round3 = {
 "round": 3, "topic": "Tauhid / Akidah",
 "title": "Manhaj Ahli Sunnah wa al-Jamaah Dalam Akidah",
 "scope": "Takrif ASWJ, 15 rukun akidah, tokoh, dan golongan bidaah",
 "mode": "Round 3 - dijawab bersama oleh kedua-dua ahli pasukan.",
 "verified": True,
 "sections": [
  {"heading": "Pengenalan & Takrif ASWJ", "points": [
   "Kitab terbitan Pejabat Mufti Wilayah Persekutuan (JAKIM), cetakan 2016 - menghuraikan akidah Ahli Sunnah wa al-Jamaah (ASWJ) secara bersistem.",
   "Sunnah: cara beragama yang diajar oleh Rasulullah SAW.",
   "Jamaah: majoriti umat Islam, khususnya para sahabat dan mereka yang mengikuti jalan sahabat - bukan sekadar mana-mana kumpulan yang mendakwa ramai.",
   "Imam Abu Hasan al-Asy'ari dan Imam Abu Mansur al-Maturidi menguatkan manhaj ASWJ dengan dalil naqli (wahyu) dan aqli (akal). Mereka TIDAK mencipta akidah baharu - hanya menyusun & mempertahankan akidah salaf.",
   "Rumusan akidah Asya'irah dan Maturidiyah ialah ajaran akidah ASWJ. Kitab ini menyusun akidah kepada 15 rukun/prinsip."]},
  {"heading": "Rukun 1 - Hakikat & Ilmu", "points": [
   "ASWJ menetapkan hakikat sesuatu dan mengiktiraf ilmu; golongan Sufastaiyyah (sofis) yang menafikan hakikat & ilmu dianggap sesat.",
   "Ilmu manusia terbahagi tiga: (1) Badihiah - diketahui tanpa penelitian; (2) Hissi - melalui pancaindera; (3) Istidlali - melalui penelitian, akal & dalil.",
   "Pancaindera: penglihatan, rasa, bau, sentuhan (panas/sejuk, basah/kering, lembut/kasar).",
   "Hadis mutawatir = jalan ilmu daruri yang sah apabila cukup syarat (contoh: pengetahuan tentang nabi & raja lampau).",
   "Ciri riwayat: mutawatir, mustafidh, dan ahad. Hadis ahad yang sahih sanad & matan serta tidak mustahil pada akal WAJIB diamalkan.",
   "Sumber hukum syariat: al-Quran, al-Sunnah dan ijmak ulama.",
   "ASWJ menolak golongan yang mengingkari ilmu mutawatir, menolak hadis ahad sahih (spt Rafidhah/Khawarij), atau mendakwa al-Quran telah diubah."]},
  {"heading": "Rukun 2 - Baharunya Alam", "points": [
   "Alam ialah SEGALA sesuatu selain Allah SWT dan sifat-sifat-Nya yang azali; semuanya makhluk yang diciptakan.",
   "Pencipta alam bukan makhluk, bukan dicipta, bukan dari jenis alam atau juzuk alam.",
   "Alam terdiri daripada jauhar (zat) dan 'arad (sifat). Jauhar al-fard tidak boleh dibahagikan lagi.",
   "Wujudnya malaikat dan syaitan sebagai makhluk dalam alam - mengingkarinya (spt ahli falsafah/Batiniah) dihukum kafir.",
   "Seluruh alam akan binasa; syurga & neraka kekal (nikmat & azabnya) melalui jalan syarak. Golongan Jahmiah yang mengajar syurga/neraka binasa dihukum kafir."]},
  {"heading": "Rukun 3 - Pencipta Alam", "points": [
   "Semua peristiwa dijadikan oleh Allah SWT. Golongan Qadariah (perbuatan tercipta sendiri tanpa pembuat) dihukum kafir.",
   "Allah pencipta jisim DAN 'arad (menolak Muammar yang kata Allah cuma cipta jisim).",
   "Allah itu Qadim (tanpa permulaan) - menolak Majusi (dua pencipta) dan pelampau Rafidhah yang mendewakan Saidina Ali.",
   "Allah tidak berpenghujung/berukuran (menolak Hisyam bin Hakam yang kata Tuhan 'tujuh jengkal').",
   "Mustahil bagi Allah mempunyai rupa & anggota seperti makhluk.",
   "Allah tidak diliputi ruang, tempat, atau peredaran masa. Kata Saidina Ali: 'Allah menjadikan Arasy untuk menzahirkan Qudrat-Nya, bukan menjadi tempat bagi Zat-Nya.'",
   "Allah Maha Kaya - tidak memerlukan pertolongan makhluk. Allah itu Esa (menolak dualisme Thanawiyah/Majusi)."]},
  {"heading": "Rukun 4 - Sifat-Sifat Allah", "points": [
   "Tujuh sifat azali & kekal: Ilmu (Maha Mengetahui), Qudrat (Maha Berkuasa), Hayat (Maha Hidup), Iradat (Maha Berkehendak), Sama' (Maha Mendengar), Basar (Maha Melihat), Kalam (Maha Berkata-kata).",
   "Muktazilah menafikan sifat-sifat azali - ditolak oleh ASWJ (menafikan sifat = menafikan zat yang disifatkan).",
   "Qudrat Allah satu, meliputi segala yang ditakdirkan.",
   "Ilmu Allah satu & azali, meliputi semua maklumat secara terperinci tanpa melalui pancaindera/istidlal (menolak Rafidhah yang kata Allah tak tahu sebelum sesuatu tercipta).",
   "Kalamullah (al-Quran) ialah sifat azali, BUKAN makhluk.",
   "Orang mukmin akan MELIHAT Allah (ru'yah) di akhirat - mengingkarinya dihukum kafir."]},
  {"heading": "Rukun 5 - Nama-Nama Allah", "points": [
   "Nama-nama Allah bersifat TAUQIFIYYAH: hanya ditetapkan berdasarkan al-Quran, Sunnah sahih, atau ijmak - tidak boleh direka melalui qias/analogi bebas.",
   "Mengetahui 99 nama Allah bukan sekadar membilang, tetapi memahami & meyakini maknanya serta beradab dengannya.",
   "Kategori nama: (1) menunjukkan Zat, (2) menunjukkan sifat azali, (3) menunjukkan perbuatan Allah (contoh al-Khaliq, al-Raziq).",
   "Contoh: al-Khaliq (Pencipta) & al-Raziq (Pemberi rezeki) menunjukkan perbuatan Allah."]},
  {"heading": "Rukun 6 - Keadilan & Hikmah Allah (Kasab)", "points": [
   "Konsep KASAB: hamba mempunyai usaha/pilihan, tetapi Allah yang menciptakan usaha & perbuatan itu.",
   "Ini jalan tengah antara dua ekstrem: Qadariah (hamba cipta perbuatan sendiri) dan Jabariah (hamba langsung tiada usaha).",
   "Hidayah dua pengertian: (1) penjelasan/seruan jalan benar - boleh disandarkan kepada Rasul & pendakwah; (2) penciptaan petunjuk dalam hati - hanya kuasa Allah.",
   "Allah Maha Adil & Maha Bijaksana dalam setiap ketentuan-Nya."]},
  {"heading": "Rukun 7 & 8 - Kenabian, Kerasulan, Mukjizat & Karamah", "points": [
   "Nabi: menerima wahyu. Rasul: menerima wahyu DAN dikhususkan dengan syariat baharu atau memansuhkan sebahagian syariat terdahulu.",
   "Para nabi lebih utama daripada malaikat dan wali.",
   "Rasul pertama Nabi Adam AS; Rasul terakhir Nabi Muhammad SAW.",
   "Mukjizat: perkara luar biasa pada NABI sebagai bukti kenabian & cabaran yang tidak dapat ditandingi. Susunan al-Quran ialah mukjizat.",
   "Karamah: perkara luar biasa yang HARUS berlaku kepada WALI - tetapi ia BUKAN bukti kenabian dan tidak menjadikan wali lebih utama daripada nabi."]},
  {"heading": "Rukun 9 & 10 - Syariat, Rukun Islam & Hukum Taklif", "points": [
   "Lima Rukun Islam: syahadah, solat, zakat, puasa Ramadan, haji.",
   "Puasa Ramadan bermula dengan rukyah hilal atau menyempurnakan 30 hari Syaaban.",
   "Sumber perundangan syariah: al-Quran, al-Sunnah, ijmak.",
   "Lima hukum taklif: WAJIB (buat berpahala, tinggal berdosa), HARAM (buat berdosa, tinggal berpahala), SUNAT (buat berpahala, tinggal tak berdosa), MAKRUH (tinggal berpahala, buat tak berdosa), HARUS (buat/tinggal tanpa pahala/dosa).",
   "Hukum taklif berkait dengan perintah & larangan Allah, bukan lintasan hati atau adat semata."]},
  {"heading": "Rukun 11 & 12 - Akhirat, Khilafah & Imamah", "points": [
   "Perkara akhirat yang wajib diimani: kebangkitan, soal & azab kubur, Mizan (timbangan amal), Sirat (titian), kolam Nabi (haudh), syafaat, syurga & neraka.",
   "Syafaat Nabi SAW & orang soleh berlaku kepada pendosa Muslim yang MASIH mempunyai iman.",
   "Imamah/khilafah diperlukan untuk menegakkan hukum, amanah, keadilan, pertahanan & pengurusan harta awam.",
   "Cara memilih pemimpin: pemilihan & ijtihad ahlul-halli wal-'aqdi.",
   "Syarat imam antaranya: ilmu, keadilan, kepimpinan, dan keutamaan Quraisy (sebagaimana disebut). Imam TIDAK disyaratkan maksum."]},
  {"heading": "Rukun 13, 14 & 15 - Iman, Wali, & Musuh Agama", "points": [
   "Asal iman: makrifah (mengenal Allah) dan pembenaran (tasdiq) dengan hati.",
   "Dosa besar TIDAK menghilangkan iman kecuali berlaku kekufuran. Pelaku dosa besar = mukmin yang fasiq (bukan kafir automatik).",
   "Para malaikat maksum daripada dosa. Susunan keutamaan: nabi > malaikat & wali.",
   "Empat Khulafa' Rasyidin termasuk 10 sahabat yang dijanjikan syurga - sahabat dihormati dan tidak dicela.",
   "Rukun 15: hukum musuh agama dibahagikan mengikut keadaan kepercayaan mereka (sebelum/selepas Islam)."]},
  {"heading": "Golongan Bidaah & Penutup", "points": [
   "Enam asal golongan yang menyeleweng: Haruriah, Qadariah, Jahmiah, Murjiah, Rafidhah (Syiah), Jabariah.",
   "Tujuan mempelajarinya: mengenal pola pemikiran yang bercanggah, melakukan TABAYYUN, dan melindungi akidah - BUKAN membuat tuduhan tanpa ilmu.",
   "Keistimewaan manhaj ASWJ: menguatkan usul agama dengan gabungan dalil NAQLI (wahyu) dan AQLI (akal).",
   "Adab menjawab soalan sensitif: berpegang pada istilah sumber, elak meluaskan hukum tanpa dalil, jawab dengan tepat & beradab."]},
  {"heading": "Ringkasan Cepat Round 3", "points": [
   "Takrif: Sunnah (ajaran Rasul) + Jamaah (majoriti sahabat & pengikut). Tokoh: al-Asy'ari & al-Maturidi.",
   "15 rukun: ilmu, baharu alam, Pencipta, sifat (7), nama (tauqifiyyah), kasab, kenabian, mukjizat/karamah, syariat, hukum taklif, akhirat, imamah, iman, wali, musuh agama.",
   "7 sifat: Ilmu, Qudrat, Hayat, Iradat, Sama', Basar, Kalam. 5 hukum taklif: wajib, haram, sunat, makruh, harus.",
   "6 golongan bidaah: Haruriah, Qadariah, Jahmiah, Murjiah, Rafidhah, Jabariah. Manhaj = naqli + aqli."]},
 ]
}

round4 = {
 "round": 4, "topic": "Akhlak",
 "title": "Kitab Penawar Bagi Hati (Syeikh Abd Qadir al-Mandili)",
 "scope": "Penyucian tujuh anggota zahir, sepuluh sifat tercela & sepuluh sifat terpuji hati",
 "mode": "Round 4 - dijawab bersama oleh kedua-dua ahli pasukan.",
 "verified": True,
 "sourceNote": "Nota ini disokong oleh alih bahasa Rumi moden bagi Kitab Penawar Bagi Hati (3 bahagian) sebagai rujukan sekunder. Naskhah asal ialah Jawi; status hadis harus disemak dengan edisi bertahkik.",
 "sections": [
  {"heading": "Pengenalan Kitab & Ilmu Tasawuf", "points": [
   "Kitab Penawar Bagi Hati karangan Syeikh Abd Qadir bin Abd Muthalib al-Mandili - kitab akhlak/tasawuf dalam tulisan Jawi.",
   "Ilmu tasawuf membincangkan KELAKUAN HATI - sama ada terpuji atau tercela - dan cara menyucikannya.",
   "Faedahnya: membersihkan hati daripada selain Allah dan menghiasinya dengan penghambaan (ubudiyyah) kepada Allah.",
   "Hukum mempelajari asas penyucian hati bagi mukallaf: fardu ain.",
   "Sumber ilmu tasawuf: al-Quran dan hadis Nabi SAW.",
   "Struktur kitab tiga bahagian besar: (1) Kitab Pertama - memelihara tujuh anggota zahir; (2) Kitab Kedua - sepuluh sifat tercela hati; (3) Bab Ketiga - sepuluh perangai yang dipuji (mengikut susunan al-Ghazali dalam al-Arba'in).",
   "Hati difahami dalam dua makna: organ jasmani, dan pusat rohani yang mengenal, memahami, berniat & menerima taklif. Hati ialah 'raja' bagi anggota - baiknya hati membawa baiknya seluruh amal."]},
  {"heading": "Kitab 1 - Tujuh Anggota: Mata", "points": [
   "Tujuh anggota yang wajib dipelihara: mata, telinga, lidah, perut, kemaluan, dua tangan, dua kaki.",
   "Manfaat akhirat mata: memandang langit, matahari, bulan, bintang sebagai dalil kebesaran Allah; membaca al-Quran; melihat jalan ke masjid & tempat ilmu.",
   "Syukur mata: memeliharanya daripada pandangan haram - memandang dengan syahwat kepada bukan halal, melihat aurat, melihat maksiat.",
   "Allah memerintahkan orang beriman menundukkan pandangan (Surah al-Nur 24:30) - ia lebih menyucikan hati.",
   "Allah mengetahui pengkhianatan mata dan apa yang tersembunyi dalam dada (Surah Ghafir 40:19).",
   "Dalam hadis: mata mempunyai bahagiannya daripada zina iaitu pandangan; kaki dengan perjalanan; tangan dengan sentuhan; hati dengan keinginan; lalu kemaluan membenarkan atau menolaknya."]},
  {"heading": "Kitab 1 - Telinga & Lidah", "points": [
   "Telinga dijadikan untuk mendengar al-Quran, hadis, ilmu bermanfaat dan nasihat - ilmu masuk ke hati melaluinya.",
   "Peliharalah telinga daripada umpatan, adu domba, bid'ah, pertengkaran, percakapan keji dan hiburan yang membawa maksiat.",
   "Perkataan yang didengar seperti makanan bagi hati: ada penawar, ada racun. Makanan keluar dari perut, tetapi perkataan buruk boleh kekal seumur hidup.",
   "Pendengaran, penglihatan dan hati akan ditanya pada hari akhirat (Surah al-Isra' 17:36).",
   "Kegunaan terpuji lidah: membaca al-Quran & hadis, berzikir, amar makruf nahi mungkar, memberi nasihat, mendamaikan manusia, urusan dunia yang harus.",
   "Umpatan (ghibah): menyebut saudara dengan sesuatu yang dibencinya jika didengar, walaupun benar - al-Quran menyamakannya dengan memakan daging saudara yang mati (Surah al-Hujurat 49:12).",
   "Tanda munafik (hadis): apabila bercakap dia berdusta, apabila berjanji dia mungkir, apabila diberi amanah dia khianat.",
   "Lidah anggota kecil tetapi luas kebinasaannya - diam lebih selamat kecuali untuk kebaikan."]},
  {"heading": "Kitab 1 - Perut, Kemaluan, Tangan & Kaki", "points": [
   "Syukur perut: menjaganya daripada makanan haram, syubhah dan berlebihan - kerana takut azab, menjaga agama & maruah.",
   "Kekenyangan berlebihan: mengeraskan hati, melemahkan kecerdasan, mengurangkan ibadah, menyebabkan mengantuk & malas, memanjangkan hisab.",
   "Had makan: sekadar menegakkan tubuh; jika perlu lebih, bahagikan 1/3 makanan, 1/3 minuman, 1/3 nafas.",
   "Kemaluan: dipelihara dengan menjaga pernikahan sah. Pemeliharaannya tidak sempurna tanpa menjaga mata, hati & perut.",
   "Al-Quran memuji orang yang memelihara kehormatan (Surah al-Mu'minun 23:5-6) dan melarang mendekati zina (Surah al-Isra' 17:32).",
   "Apabila manusia mati, amalnya terputus kecuali tiga: sedekah jariah, ilmu bermanfaat, anak soleh yang mendoakan.",
   "Tangan & kaki: kaki menuju masjid, ilmu, jihad, haji, silaturahim; tangan mencegah mungkar, menulis ilmu. Jangan menyakiti, mengkhianati amanah, mengambil haram, atau menulis sihir/ilmu haram."]},
  {"heading": "Kitab 2 - Sifat Tercela: Rakus Makan & Banyak Cakap", "points": [
   "Kitab Kedua menyenaraikan SEPULUH sifat tercela hati.",
   "1) Rakus terhadap makanan (syarah al-ta'am): akar banyak kejahatan - perut jadi pintu kepada syahwat, cinta harta, kemegahan, lalu riak/takbur/dengki.",
   "Faedah lapar: melembutkan hati, menambah kesediaan ibadah, membantu kecerdasan, melemahkan nafsu, meringankan tubuh, menimbulkan belas kepada orang miskin.",
   "Rawatan rakus makan: kurangkan secara BERANSUR-ANSUR (bukan mendadak), berhenti sebelum kenyang, niatkan makanan sebagai bekal taat.",
   "2) Banyak berkata-kata: percakapan melebihi manfaat - membawa dusta, mengumpat, buka aib, pertengkaran, pujian melampau.",
   "Tiga tapisan sebelum bercakap: BENAR, PERLU, dan BAIK. Biasakan diam bila tiada manfaat."]},
  {"heading": "Kitab 2 - Marah, Dengki, Kikir", "points": [
   "3) Marah: tenaga yang boleh mempertahankan kebenaran, tetapi jadi penyakit bila nafsu menguasainya - melahirkan makian, dendam, permusuhan.",
   "Rawatan marah: baca isti'azah (a'uzubillah), ubah posisi (berdiri->duduk->baring), ambil wuduk, latih pemaafan.",
   "4) Dengki (hasad): tidak senang dengan nikmat orang lain dan mahu ia HILANG. Berbeza dengan GHIBTAH: ingin kebaikan yang sama TANPA berharap nikmat orang lain lenyap.",
   "Bahaya dengki: menyeksa diri (nikmat orang tak berkurang), merosakkan pahala, membantah pembahagian kurniaan Allah. Rawatan: doakan kebaikan orang itu, puji kebaikannya, tukar dengki kepada ghibtah.",
   "5) Kikir (bakhil): menahan pemberian yang dituntut syarak/maruah. Cinta harta jadi penyakit bila harta menguasai hati.",
   "Rawatan kikir: tunaikan hak wajib dahulu (zakat, nafkah, hutang), tetapkan sedekah berkala, ambil sekadar keperluan."]},
  {"heading": "Kitab 2 - Kemegahan, Cinta Dunia, Takbur, Ujub, Riyak", "points": [
   "6) Cinta kemasyhuran/pengaruh: mahu menguasai hati manusia melalui pangkat & nama. Kedudukan tidak tercela jika untuk menolak kezaliman & membawa manfaat.",
   "7) Cinta dunia: keterikatan pada perkara yang tidak bermanfaat selepas mati. Dunia jadi ladang akhirat bila digunakan untuk taat. Nilai setiap urusan: 'adakah ia bermanfaat selepas mati?'",
   "8) Takbur: melihat diri lebih sempurna & orang lain lebih rendah. Tanda utama: MENOLAK KEBENARAN & merendahkan manusia. Rawatan: kenal kelemahan diri, terima nasihat walau daripada yang lebih muda.",
   "9) Ujub: kagum terhadap diri/amal sendiri sambil lupa ia kurniaan Allah. Beza dengan takbur: takbur perlu orang lain untuk direndahkan; ujub boleh berlaku walau BERSENDIRIAN.",
   "10) Riyak: beramal untuk mendapat kedudukan/pujian manusia - digelar SYIRIK KECIL kerana tujuan amal dialih daripada Allah kepada makhluk.",
   "Rawatan riyak: sembunyikan amal bila tiada maslahat; JANGAN tinggalkan ibadah kerana takut riyak - teruskan sambil lawan niat salah; perbaharui niat sebelum, semasa & selepas amal."]},
  {"heading": "Bab 3 - Sifat Terpuji: Taubat, Khauf, Zuhud", "points": [
   "Bab Ketiga menyenaraikan SEPULUH perangai terpuji mengikut susunan al-Ghazali (al-Arba'in).",
   "1) Taubat: permulaan jalan menuju akhirat. Rukun taubat TIGA: menyesal kerana Allah, meninggalkan maksiat, berazam tidak mengulangi.",
   "Jika dosa berkait hak manusia - pulangkan/ganti/minta halal. Taubat diterima selagi nyawa belum ke halkum & sebelum matahari terbit dari barat.",
   "2) Takut kepada Allah (khauf): rasa gementar menjangka perkara dibenci. Takut yang sempurna lahir daripada MENGENAL kebesaran Allah - 'semakin dalam ilmu, semakin kuat takut'.",
   "Takut mesti mendorong amal, BUKAN melumpuhkan sehingga putus asa - hendaklah seimbang dengan harapan (raja').",
   "3) Zuhud: hati tidak tertarik kepada dunia yang melalaikan. Zuhud BUKAN semata-mata miskin - orang berharta boleh zuhud jika harta tidak menguasai hatinya.",
   "Tiga sebab zuhud: takut neraka (zuhud orang takut), inginkan syurga (zuhud orang berharap), membesarkan Allah (zuhud orang yang mengenal Allah - tertinggi)."]},
  {"heading": "Bab 3 - Sabar, Syukur, Ikhlas", "points": [
   "4) Sabar: menahan diri daripada hawa nafsu, menetapkan hati pada agama. Tiga jenis: sabar dalam ketaatan, sabar meninggalkan maksiat, sabar menghadapi musibah.",
   "Sabar pada maksiat sering paling sukar (keinginan datang dari dalam & berulang). Kesedihan TIDAK bercanggah dengan sabar selagi tiada bantahan terhadap Allah.",
   "5) Syukur: menggunakan setiap nikmat pada tujuan ia diciptakan - bukan sekadar puji dengan lidah. Tiga unsur: tahu nikmat dari Allah, gembira kepada Pemberi, guna nikmat dalam taat.",
   "Syukur tiga peringkat: hati (mengenal & merendah diri), lidah (memuji tanpa riak), anggota (guna untuk taat). Nikmat agama lebih utama daripada nikmat dunia.",
   "6) Ikhlas: memurnikan tujuan amal hanya untuk Allah. Niat asas kerana nilai amal bergantung pada tujuan dalam hati.",
   "Menyembunyikan amal lebih selamat. JANGAN tinggalkan amal kerana takut dikata riak - itu juga satu bentuk perhatian kepada manusia. Perbaharui niat sebelum, semasa & selepas amal."]},
  {"heading": "Bab 3 - Tawakal, Mahabbah, Reda, Ingat Mati", "points": [
   "7) Tawakal: menyerahkan hati kepada Allah SETELAH mengambil sebab yang dibenarkan - BUKAN meninggalkan usaha. Anggota bekerja, hati bersandar kepada Allah.",
   "Tiga tingkat tawakal: percaya Allah seperti wakil cekap; serah diri seperti anak kepada ibu; hati seperti mayat di tangan pemandi (tertinggi) - tanpa membantah, sambil patuh syarak.",
   "8) Kasih kepada Allah (mahabbah): kedudukan tinggi mengikuti makrifat. Allah dicintai kerana zat, sifat & nikmat-Nya. Tanda: mendahulukan perintah Allah, rindu bertemu-Nya, banyak zikir, cinta Rasul & orang taat.",
   "Orang yang benar mencintai Allah tidak mendakwa kesempurnaan - kasih dibuktikan dengan KETAATAN & mengikut Rasul.",
   "9) Reda dengan qada Allah: hati menerima ketentuan Allah tanpa membantah. Reda TIDAK bererti hilang rasa sakit, atau tinggalkan doa/rawatan/usaha.",
   "Orang dahaga tetap cari air; orang sakit tetap berubat - ini sebab yang diperintah & tidak bercanggah dengan reda. Kasih kepada Allah memudahkan reda.",
   "10) Mengingati mati: memendekkan angan-angan & mendorong persediaan akhirat. Cara: ziarah kubur, hadiri orang sakit, renung perubahan tubuh. Setiap pagi & petang peluang perbaharui taubat."]},
  {"heading": "Rancangan Penyucian Bersepadu & Ringkasan", "points": [
   "Kesepuluh penyakit saling berkait: rakus makan menguatkan syahwat & cinta dunia; cinta dunia mendorong cinta harta & kemegahan; kemegahan melahirkan takbur, ujub & riak.",
   "Penyucian hati BUKAN menghapus setiap naluri - lapar, cakap, marah, harta, kedudukan boleh membawa kebaikan. Matlamatnya: membawa setiap naluri di bawah ilmu, akal, wahyu & niat ikhlas.",
   "Tanda kemajuan terkuat BUKAN dakwaan suci, tetapi bertambahnya tawaduk, kawalan diri, kemurahan, kesyukuran & keistiqamahan amal zahir & batin.",
   "7 anggota: mata, telinga, lidah, perut, kemaluan, 2 tangan, 2 kaki. Perut: 1/3 makan, 1/3 minum, 1/3 nafas.",
   "10 tercela: rakus makan, banyak cakap, marah, dengki, kikir, cinta kemegahan, cinta dunia, takbur, ujub, riyak.",
   "10 terpuji: taubat, khauf, zuhud, sabar, syukur, ikhlas, tawakal, mahabbah, reda, ingat mati.",
   "Ingat: dengki (mahu nikmat hilang) vs ghibtah (mahu serupa); takbur (perlu orang lain) vs ujub (bersendirian); tawakal & reda = SELEPAS usaha, bukan tinggalkan usaha."]},
 ]
}

data["books"] = [round1, round2, round3, round4]
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

for b in data["books"]:
    print(f"Round {b['round']}: {len(b['sections'])} sections, "
          f"{sum(len(s['points']) for s in b['sections'])} points")
print("Wrote", OUT)
