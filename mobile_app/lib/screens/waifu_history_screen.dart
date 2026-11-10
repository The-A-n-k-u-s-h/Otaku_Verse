import 'package:flutter/material.dart';
import '../models/waifu_history_model.dart';
import '../services/waifu_history_service.dart';
import 'waifu_history_detail_screen.dart';

class WaifuHistoryScreen extends StatefulWidget {
  const WaifuHistoryScreen({super.key});

  @override
  State<WaifuHistoryScreen> createState() => _WaifuHistoryScreenState();
}

class _WaifuHistoryScreenState extends State<WaifuHistoryScreen> {
  final _service = WaifuHistoryService.instance;
  late Future<List<WaifuHistoryItem>> _future;

  @override
  void initState() {
    super.initState();
    _future = _service.getHistory();
  }

  Future<void> _refresh() async {
    final request = _service.getHistory();
    setState(() => _future = request);
    await request;
  }

  Future<void> _delete(WaifuHistoryItem item) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete match?'),
        content: Text('Remove ${item.characterName} from your history?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    try {
      await _service.deleteHistory(item.id);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('History item deleted.')),
      );
      await _refresh();
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not delete item: $error')),
      );
    }
  }

  Future<void> _clearAll() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear all history?'),
        content: const Text('This permanently deletes all saved matches.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Clear all'),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    try {
      await _service.clearHistory();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Match history cleared.')),
      );
      await _refresh();
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not clear history: $error')),
      );
    }
  }

  Widget _score(String label, double score) => Chip(
        label: Text('$label ${score.toStringAsFixed(0)}%'),
        visualDensity: VisualDensity.compact,
      );

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Waifu Match History'),
        actions: [
          IconButton(
            tooltip: 'Clear all history',
            onPressed: _clearAll,
            icon: const Icon(Icons.delete_sweep_outlined),
          ),
        ],
      ),
      body: FutureBuilder<List<WaifuHistoryItem>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return _MessageState(
              message: 'Could not load history.\n${snapshot.error}',
              onRetry: _refresh,
            );
          }
          final items = snapshot.data ?? [];
          if (items.isEmpty) {
            return const _MessageState(
              message: 'No saved matches yet. Complete a Waifu Match to see it here.',
            );
          }
          return RefreshIndicator(
            onRefresh: _refresh,
            child: ListView.separated(
              padding: const EdgeInsets.all(16),
              itemCount: items.length,
              separatorBuilder: (_, _) => const SizedBox(height: 12),
              itemBuilder: (context, index) {
                final item = items[index];
                return Card(
                  clipBehavior: Clip.antiAlias,
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(12),
                    leading: item.imageUrl.isEmpty
                        ? const CircleAvatar(child: Icon(Icons.favorite))
                        : CircleAvatar(
                            radius: 29,
                            backgroundImage: NetworkImage(item.imageUrl),
                            onBackgroundImageError: (_, _) {},
                            child: null,
                          ),
                    title: Text(
                      item.characterName,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(item.animeTitle),
                        const SizedBox(height: 5),
                        Wrap(
                          spacing: 4,
                          children: [
                            _score('Overall', item.overallScore),
                            _score('Personality', item.personalityScore),
                            _score('Romantic', item.romanticScore),
                          ],
                        ),
                        if (item.createdAt.isNotEmpty)
                          Text(
                            item.createdAt,
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                      ],
                    ),
                    isThreeLine: true,
                    trailing: PopupMenuButton<String>(
                      onSelected: (value) {
                        if (value == 'delete') _delete(item);
                      },
                      itemBuilder: (_) => const [
                        PopupMenuItem(
                          value: 'delete',
                          child: Text('Delete'),
                        ),
                      ],
                    ),
                    onTap: () async {
                      await Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) =>
                              WaifuHistoryDetailScreen(historyId: item.id),
                        ),
                      );
                    },
                  ),
                );
              },
            ),
          );
        },
      ),
    );
  }
}

class _MessageState extends StatelessWidget {
  final String message;
  final Future<void> Function()? onRetry;

  const _MessageState({required this.message, this.onRetry});

  @override
  Widget build(BuildContext context) => Center(
        child: Padding(
          padding: const EdgeInsets.all(28),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.history_rounded, size: 48),
              const SizedBox(height: 12),
              Text(message, textAlign: TextAlign.center),
              if (onRetry != null) ...[
                const SizedBox(height: 14),
                FilledButton(
                  onPressed: onRetry,
                  child: const Text('Try again'),
                ),
              ],
            ],
          ),
        ),
      );
}
