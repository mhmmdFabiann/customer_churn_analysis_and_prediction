# Business Analytics Findings & Strategic Recommendations

**Track:** Data Analytics (DA)  
**Dokumen Pendukung:** Visualisasi di `reports/figures/` dan Kueri SQL di `sql/`

---

## 1. Temuan Kunci Analitik Bisnis

### Temuan 1: Volatilitas Akut pada Kontrak Month-to-Month
- **Bukti Kuantitatif:** Sebanyak **88,6%** dari total 1.869 pelanggan yang churn memegang kontrak *Month-to-month* (churn rate kelompok ini mencapai **42,71%**). Sebagai perbandingan, churn rate pada kontrak 1 tahun hanya 11,27% dan kontrak 2 tahun hanya 2,83%.
- **Dampak Finansial:** Kehilangan pendapatan bulanan (*MRR Loss*) dari kelompok kontrak bulanan mencapai **$123.414,80/bulan** (88,7% dari total seluruh kerugian churn perusahaan).
- **Interpretasi:** Kontrak bulanan memberikan fleksibilitas tinggi tanpa friksi peralihan (*switching barrier*), sehingga pelanggan mudah tergoda penawaran promosi kompetitor.

### Temuan 2: The "Danger Zone" pada Siklus Hidup 0–12 Bulan Pertama
- **Bukti Kuantitatif:** Median masa berlangganan (*tenure*) pelanggan yang churn hanya **10 bulan** (berbanding pelanggan loyal yang memiliki median **38 bulan**). Pada pelanggan baru (0–12 bulan) dengan kontrak bulanan, tingkat churn mencapai **53,8%**.
- **Interpretasi:** Retensi jangka panjang ditentukan pada 90 hingga 180 hari pertama. Jika pelanggan berhasil dipertahankan melewati tahun pertama, probabilitas loyalitas melonjak signifikan.

### Temuan 3: Paradoks Layanan Fiber Optic (High ARPU, High Churn)
- **Bukti Kuantitatif:** Pelanggan Fiber Optic menyumbang churn tertinggi (**41,89%**) dengan rata-rata tagihan bulanan tertinggi ($91,50/bulan). Ketika pelanggan Fiber Optic **tidak memiliki Tech Support**, tingkat churn melonjak hingga **53,3%**.
- **Interpretasi:** Pelanggan yang membayar harga premium memiliki toleransi rendah terhadap gangguan teknis. Beban biaya tinggi yang tidak diimbangi dengan pendampingan teknis memicu keputusan pemutusan layanan.

### Temuan 4: Risiko Tinggi pada Metode Pembayaran Electronic Check
- **Bukti Kuantitatif:** Pelanggan dengan metode pembayaran *Electronic check* mengalami churn rate **45,29%**, dibandingkan metode otomatis *Auto-pay* via kartu kredit (15,24%) atau transfer bank (16,71%).
- **Interpretasi:** Pembayaran manual mengharuskan pelanggan mereviu tagihan setiap bulan secara aktif, memperbesar peluang evaluasi untuk berhenti langganan.

---

## 2. Rekomendasi Strategis Berbasis Data

1. **Kampanye Insentif Migrasi Kontrak Tahunan (Quick Win):**
   - Tawarkan diskon biaya langganan bulanan 10%–15% atau bonus upgrade kuota/kecepatan bagi pelanggan *Month-to-month* yang bersedia beralih ke kontrak komitmen 1 tahun.
2. **Paket Bundling 'Value-Shield' Fiber Optic:**
   - Berikan add-on *Tech Support* dan *Online Security* gratis selama 3–6 bulan pertama bagi seluruh pelanggan baru Fiber Optic.
3. **Program Retensi Onboarding (Hari ke-7, 30, dan 60):**
   - Lakukan penjangkauan proaktif untuk memvalidasi kepuasan instalasi dan kestabilan koneksi di bulan-bulan awal.
4. **Program Reward Transisi ke Auto-Pay:**
   - Berikan diskon tagihan satu kali sebesar $5 bagi pelanggan yang beralih dari *Electronic check* ke autodebet kartu kredit atau transfer bank.
