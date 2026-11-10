import 'package:flutter/material.dart';
import '../models/waifu_history_model.dart';
import '../services/waifu_history_service.dart';

class WaifuHistoryDetailScreen extends StatefulWidget {
  final int historyId;
  const WaifuHistoryDetailScreen({super.key, required this.historyId});

  @override
  State<WaifuHistoryDetailScreen> createState() =>
      _WaifuHistoryDetailScreenState();
}

class _WaifuHistoryDetailScreenState
    extends State<WaifuHistoryDetailScreen> {
  late Future<WaifuHistoryDetail> _future;

  @override
  void initState() {
    super.initState();
    _future = WaifuHistoryService.instance.getDetail(widget.historyId);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Match Details')),
      body: FutureBuilder<WaifuHistoryDetail>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Text('Could not load match details.\n${snapshot.error}'),
              ),
            );
          }
          final detail = snapshot.data!;
          final item = detail.item;
          final character = detail.snapshot['character'] is Map
              ? Map<String, dynamic>.from(detail.snapshot['character'])
              : <String, dynamic>{};
          final explanation = detail.explanation;

          Widget score(String title, double value) => ListTile(
                title: Text(title),
                trailing: Text(
                  '${value.toStringAsFixed(1)}%',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              );

          Widget explanationText(String key, String fallback) {
            final value = explanation[key]?.toString().trim() ?? '';
            if (value.isEmpty) return const SizedBox.shrink();
            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    key.replaceAll('_', ' ').toUpperCase(),
                    style: Theme.of(context).textTheme.labelLarge,
                  ),
                  const SizedBox(height: 4),
                  Text(value),
                ],
              ),
            );
          }

          return ListView(
            padding: const EdgeInsets.all(18),
            children: [
              if (item.imageUrl.isNotEmpty)
                ClipRRect(
                  borderRadius: BorderRadius.circular(18),
                  child: Image.network(
                    item.imageUrl,
                    height: 260,
                    fit: BoxFit.cover,
                    errorBuilder: (_, _, _) => const SizedBox(
                      height: 120,
                      child: Center(child: Icon(Icons.broken_image_outlined)),
                    ),
                  ),
                ),
              const SizedBox(height: 16),
              Text(
                item.characterName,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
              ),
              Text(item.animeTitle),
              if ((character['description'] ?? '').toString().isNotEmpty) ...[
                const SizedBox(height: 10),
                Text(character['description'].toString()),
              ],
              const SizedBox(height: 18),
              Text('Compatibility scores',
                  style: Theme.of(context).textTheme.titleLarge),
              score('Overall compatibility', item.overallScore),
              score('Personality compatibility', item.personalityScore),
              score('Romantic compatibility', item.romanticScore),
              const Divider(height: 28),
              Text('AI explanation',
                  style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 12),
              explanationText('headline', ''),
              explanationText('summary', ''),
              explanationText('personality_reason', ''),
              explanationText('romantic_reason', ''),
              explanationText('compatibility_message', ''),
              if (explanation.isEmpty)
                const Text('No explanation was saved for this match.'),
              if (explanation['strongest_connections'] is List) ...[
                const SizedBox(height: 8),
                const Text(
                  'Strongest connections',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                for (final value
                    in explanation['strongest_connections'] as List)
                  ListTile(
                    dense: true,
                    leading: const Icon(Icons.check_circle_outline),
                    title: Text(value.toString()),
                  ),
              ],
              if (item.createdAt.isNotEmpty) ...[
                const Divider(height: 28),
                Text('Saved: ${item.createdAt}'),
              ],
            ],
          );
        },
      ),
    );
  }
}
