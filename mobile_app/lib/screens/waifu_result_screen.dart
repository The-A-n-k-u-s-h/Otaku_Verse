import 'package:flutter/material.dart';
import '../models/waifu_result_model.dart';
import '../services/waifu_result_service.dart';

class WaifuResultScreen extends StatefulWidget {
  const WaifuResultScreen({super.key});

  @override
  State<WaifuResultScreen> createState() => _WaifuResultScreenState();
}

class _WaifuResultScreenState extends State<WaifuResultScreen> {
  late Future<WaifuMatchResult> _resultFuture;

  @override
  void initState() {
    super.initState();
    _resultFuture = WaifuResultService.instance.fetchResult();
  }

  void _retry() {
    setState(() {
      _resultFuture = WaifuResultService.instance.fetchResult();
    });
  }

  Widget _score(String label, double value) => Expanded(
    child: Card(child: Padding(
      padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 8),
      child: Column(children: [
        Text('${value.toStringAsFixed(1)}%',
          style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 19)),
        const SizedBox(height: 4),
        Text(label, textAlign: TextAlign.center,
          style: const TextStyle(fontSize: 11)),
      ]),
    )),
  );

  Widget _section(String title, String body) {
    if (body.trim().isEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(top: 14),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: const TextStyle(fontWeight: FontWeight.w800, fontSize: 16)),
        const SizedBox(height: 5),
        Text(body),
      ]),
    );
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Your Waifu Match')),
    body: FutureBuilder<WaifuMatchResult>(
      future: _resultFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          return Center(child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              const Icon(Icons.error_outline, size: 48),
              const SizedBox(height: 12),
              Text(snapshot.error.toString(), textAlign: TextAlign.center),
              const SizedBox(height: 12),
              FilledButton(onPressed: _retry, child: const Text('Try again')),
            ]),
          ));
        }

        final result = snapshot.data!;
        final explanation = result.explanation;
        final connections = explanation['strongest_connections'];
        return ListView(padding: const EdgeInsets.all(18), children: [
          const Text('YOUR BEST MATCH',
            textAlign: TextAlign.center,
            style: TextStyle(letterSpacing: 2, fontWeight: FontWeight.w900)),
          const SizedBox(height: 14),
          if (result.imageUrl.isNotEmpty)
            ClipRRect(
              borderRadius: BorderRadius.circular(20),
              child: Image.network(
                result.imageUrl,
                height: 300,
                width: double.infinity,
                fit: BoxFit.cover,
                errorBuilder: (_, _, _) => Container(
                  height: 180,
                  alignment: Alignment.center,
                  color: Theme.of(context).colorScheme.surfaceContainerHighest,
                  child: const Icon(Icons.image_not_supported, size: 52),
                ),
              ),
            ),
          const SizedBox(height: 16),
          Text(result.characterName,
            textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.w900)),
          Text(result.animeTitle, textAlign: TextAlign.center,
            style: Theme.of(context).textTheme.titleMedium),
          if (result.description.isNotEmpty)
            Padding(padding: const EdgeInsets.only(top: 12),
              child: Text(result.description)),
          const SizedBox(height: 12),
          Row(children: [
            _score('Overall', result.overallScore),
            _score('Personality', result.personalityScore),
            _score('Romantic', result.romanticScore),
          ]),
          Card(child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text('${explanation['headline'] ?? 'Why you match'}',
                style: Theme.of(context).textTheme.titleLarge),
              _section('Your match explained',
                '${explanation['summary'] ?? ''}'),
              _section('Personality connection',
                '${explanation['personality_reason'] ?? ''}'),
              _section('Romantic compatibility',
                '${explanation['romantic_reason'] ?? ''}'),
              if (connections is List && connections.isNotEmpty) ...[
                _section('Strongest connections', connections.map((e) => '• $e').join('\n')),
              ],
              _section('A message for you',
                '${explanation['compatibility_message'] ?? ''}'),
              const SizedBox(height: 10),
              Text('Explanation: ${result.explanationSource}',
                style: Theme.of(context).textTheme.bodySmall),
            ]),
          )),
          const Padding(
            padding: EdgeInsets.only(top: 12),
            child: Text(
              'This is an entertainment-based compatibility estimate, not a scientific or psychological assessment.',
              textAlign: TextAlign.center,
            ),
          ),
        ]);
      },
    ),
  );
}
