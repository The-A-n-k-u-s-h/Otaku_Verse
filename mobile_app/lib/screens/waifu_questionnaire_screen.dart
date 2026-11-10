import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/material.dart';
import '../models/waifu_question_model.dart';
import '../services/waifu_service.dart';
import 'waifu_result_screen.dart';

class WaifuQuestionnaireScreen extends StatefulWidget {
  const WaifuQuestionnaireScreen({super.key});

  @override
  State<WaifuQuestionnaireScreen> createState() =>
      _WaifuQuestionnaireScreenState();
}

class _WaifuQuestionnaireScreenState extends State<WaifuQuestionnaireScreen> {
  final WaifuService _service = WaifuService.instance;
  final AudioPlayer _audioPlayer = AudioPlayer();
  WaifuQuestion? _question;
  WaifuProgress? _progress;
  int? _selectedOptionId;
  bool _loading = false;
  bool _started = false;
  bool _completed = false;
  String? _error;
  Map<String, dynamic>? _profiles;

  String _cleanError(Object error) =>
      error.toString().replaceFirst('Exception: ', '');

  @override
  void dispose() {
    _audioPlayer.dispose();
    super.dispose();
  }

  Future<void> _playAudio(String url) async {
    if (url.isEmpty) return;
    try {
      await _audioPlayer.stop();
      await _audioPlayer.play(UrlSource(url));
    } catch (error) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not play audio: $error')),
      );
    }
  }

  Future<void> _start() async {
    setState(() {
      _loading = true;
      _error = null;
      _completed = false;
      _profiles = null;
      _selectedOptionId = null;
    });
    try {
      final result = await _service.startQuestionnaire();
      if (!mounted) return;
      setState(() {
        _started = true;
        _question = result.question;
        _progress = result.progress;
        _completed = result.question == null;
      });
      if (result.question == null) await _loadProfiles();
    } catch (error) {
      if (mounted) setState(() => _error = _cleanError(error));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _resume() async {
    setState(() { _loading = true; _error = null; });
    try {
      final question = await _service.getNextQuestion();
      if (!mounted) return;
      setState(() {
        _started = true;
        _question = question;
        _completed = question == null;
      });
      if (question == null) await _loadProfiles();
    } catch (error) {
      if (mounted) setState(() => _error = _cleanError(error));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _submit() async {
    final question = _question;
    final optionId = _selectedOptionId;
    if (question == null || optionId == null || _loading) return;
    setState(() { _loading = true; _error = null; });
    try {
      final result = await _service.submitAnswer(
        questionId: question.id, optionId: optionId);
      if (!mounted) return;
      setState(() {
        _progress = result.progress;
        _question = result.nextQuestion;
        _selectedOptionId = null;
        _completed = result.completed;
      });
      if (result.completed) await _loadProfiles();
    } catch (error) {
      if (mounted) setState(() => _error = _cleanError(error));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _loadProfiles() async {
    try {
      final data = await _service.getProfiles();
      if (!mounted) return;
      setState(() => _profiles = data['profiles'] is Map
          ? Map<String, dynamic>.from(data['profiles'])
          : <String, dynamic>{});
    } catch (error) {
      if (mounted) setState(() => _error = _cleanError(error));
    }
  }

  Future<void> _openResult() async {
    await Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => const WaifuResultScreen()),
    );
  }

  Widget _media(WaifuMedia media, {double height = 190}) {
    final visual = media.visualUrl;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (visual.isNotEmpty)
          ClipRRect(
            borderRadius: BorderRadius.circular(14),
            child: Image.network(
              visual,
              height: height,
              fit: BoxFit.cover,
              errorBuilder: (_, _, _) => Container(
                height: height,
                alignment: Alignment.center,
                color: Theme.of(context).colorScheme.surfaceContainerHighest,
                child: const Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.broken_image_outlined),
                    SizedBox(height: 5),
                    Text('Media unavailable'),
                  ],
                ),
              ),
            ),
          ),
        if (media.audioUrl.isNotEmpty)
          Align(
            alignment: Alignment.centerLeft,
            child: TextButton.icon(
              onPressed: () => _playAudio(media.audioUrl),
              icon: const Icon(Icons.volume_up),
              label: const Text('Play audio'),
            ),
          ),
      ],
    );
  }

  Widget _progressCard() {
    final p = _progress!;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
              const Text('Your progress',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              Text('${p.answered}/${p.availableQuestions}'),
            ]),
            const SizedBox(height: 10),
            LinearProgressIndicator(value: p.fraction),
            Wrap(spacing: 8, children: [
              Chip(label: Text('Personality: ${p.personalityAnswers}')),
              Chip(label: Text('Romantic: ${p.romanticAnswers}')),
            ]),
          ],
        ),
      ),
    );
  }

  Widget _questionCard() {
    final q = _question;
    if (q == null) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Text('No approved unanswered questions are available. Ask the operator to approve questions for both profiles.'),
        ),
      );
    }
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(q.profileType.toUpperCase(),
                style: const TextStyle(
                    fontWeight: FontWeight.bold, color: Colors.deepPurple)),
            if (q.difficulty.isNotEmpty)
              Text('Difficulty: ${q.difficulty}',
                  style: Theme.of(context).textTheme.labelSmall),
            const SizedBox(height: 10),
            Text(q.prompt, style: Theme.of(context).textTheme.titleLarge),
            _media(q.media, height: 210),
            const SizedBox(height: 8),
            for (final option in q.options)
              Card(
                child: RadioListTile<int>(
                  value: option.id,
                  groupValue: _selectedOptionId,
                  onChanged: _loading
                      ? null
                      : (value) => setState(() => _selectedOptionId = value),
                  title: Text(option.text),
                  subtitle: option.media.visualUrl.isEmpty &&
                          option.media.audioUrl.isEmpty
                      ? null
                      : Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (option.media.visualUrl.isNotEmpty)
                              _media(option.media, height: 135),
                            if (option.media.visualUrl.isEmpty &&
                                option.media.audioUrl.isNotEmpty)
                              TextButton.icon(
                                onPressed: () =>
                                    _playAudio(option.media.audioUrl),
                                icon: const Icon(Icons.volume_up),
                                label: const Text('Play answer audio'),
                              ),
                          ],
                        ),
                ),
              ),
            const SizedBox(height: 10),
            SizedBox(
              width: double.infinity,
              child: FilledButton(
                onPressed:
                    _loading || _selectedOptionId == null ? null : _submit,
                child: _loading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Submit answer'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _completedCard() {
    final profiles = _profiles;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Icon(Icons.check_circle, color: Colors.green, size: 40),
            Text('Your profiles are complete',
                style: Theme.of(context).textTheme.titleLarge),
            const Text('Your personality and romantic preference profiles have been saved by the backend.'),
            if (profiles != null)
              for (final type in ['personality', 'romantic'])
                ExpansionTile(
                  title: Text(type == 'personality'
                      ? 'Personality profile'
                      : 'Romantic profile'),
                  children: [
                    if (profiles[type] is Map)
                      for (final entry
                          in Map<String, dynamic>.from(profiles[type] as Map)
                              .entries)
                        ListTile(
                          title: Text(entry.key.replaceAll('_', ' ')),
                          trailing: Text(entry.value is Map
                              ? '${entry.value['score'] ?? 0}/100'
                              : '${entry.value}'),
                        ),
                  ],
                ),
            const SizedBox(height: 10),
            FilledButton.icon(
              onPressed: _loading ? null : _openResult,
              icon: const Icon(Icons.favorite),
              label: const Text('View my Waifu match'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Text('AI Waifu Match',
              style: Theme.of(context).textTheme.headlineSmall),
          const Text('Answer questions to build your personality and romantic preference profiles.'),
          const SizedBox(height: 16),
          if (_progress != null) _progressCard(),
          if (_error != null)
            Card(
              color: Theme.of(context).colorScheme.errorContainer,
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Text(_error!),
              ),
            ),
          const SizedBox(height: 12),
          if (!_started)
            Wrap(
              spacing: 8,
              children: [
                FilledButton(
                  onPressed: _loading ? null : _start,
                  child: const Text('Start questionnaire'),
                ),
                OutlinedButton(
                  onPressed: _loading ? null : _resume,
                  child: const Text('Resume session'),
                ),
              ],
            )
          else if (_completed)
            _completedCard()
          else
            _questionCard(),
        ],
      );
}
