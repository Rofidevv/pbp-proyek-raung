import 'package:flutter/material.dart';

class FormLaporScreen extends StatefulWidget {
  const FormLaporScreen({super.key, required this.ruang});

  final String ruang;

  @override
  State<FormLaporScreen> createState() => _FormLaporScreenState();
}

class _FormLaporScreenState extends State<FormLaporScreen> {
  final _formKey = GlobalKey<FormState>();

  void _kirim() {
    if (!_formKey.currentState!.validate()) return;
    // Penyimpanan baru ada di R-02/R-05; pesan ini sengaja jujur.
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Belum tersambung ke server; laporan belum disimpan.')),
    );
    Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Form Lapor')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextFormField(
              initialValue: widget.ruang,
              readOnly: true,
              decoration: const InputDecoration(labelText: 'Ruang'),
            ),
            TextFormField(
              decoration: const InputDecoration(labelText: 'Judul'),
              validator: (v) => (v == null || v.trim().isEmpty) ? 'Judul wajib diisi' : null,
            ),
            TextFormField(
              decoration: const InputDecoration(labelText: 'Deskripsi'),
              maxLines: 4,
            ),
            const SizedBox(height: 16),
            FilledButton(onPressed: _kirim, child: const Text('Kirim')),
          ],
        ),
      ),
    );
  }
}
