import 'package:flutter/material.dart';

import '../models/feature_model.dart';
import '../services/api_service.dart';
import '../widgets/feature_card.dart';

class HomeScreen extends StatefulWidget {
  final bool isDark;
  final VoidCallback onToggleTheme;

  const HomeScreen({
    super.key,
    required this.isDark,
    required this.onToggleTheme,
  });

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  // The landing page is shown first. Selecting a bottom tab opens that feature.
  int _currentTab = 0;
  bool _showingLanding = true;
  bool _guestLoading = false;
  int? _guestDuration;

  Future<void> _startGuestSession(int duration) async {
    if (_guestLoading) return;

    setState(() => _guestLoading = true);

    try {
      final result = await ApiService.instance.startGuestSession(duration);
      if (!mounted) return;

      setState(() => _guestDuration = duration);

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            result['message']?.toString() ??
                'Your $duration-minute guest session has started.',
          ),
        ),
      );
    } catch (error) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Could not start guest session: $error'),
          backgroundColor: Colors.red.shade700,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _guestLoading = false);
      }
    }
  }

  void _showGuestOptions() {
    showModalBottomSheet<void>(
      context: context,
      showDragHandle: true,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).colorScheme.surface,
      builder: (sheetContext) {
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(22, 8, 22, 24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Continue as Guest',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 7),
                const Text('Choose how long you want to explore.'),
                const SizedBox(height: 18),
                for (final minutes in const [10, 20, 30])
                  Padding(
                    padding: const EdgeInsets.only(bottom: 9),
                    child: SizedBox(
                      width: double.infinity,
                      child: FilledButton.tonal(
                        onPressed: _guestLoading
                            ? null
                            : () {
                                Navigator.pop(sheetContext);
                                _startGuestSession(minutes);
                              },
                        child: Text('$minutes minutes'),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        );
      },
    );
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  void _openFeature(int index) {
    if (index < 0 || index >= otakuFeatures.length) return;

    setState(() {
      _currentTab = index;
      _showingLanding = false;
    });
  }

  void _showAuthMessage(String action) {
    _showMessage(
      '$action is not connected yet. Connect this button to your Flask authentication API.',
    );
  }

  Widget _buildHeader() {
    final textColor = Theme.of(context).colorScheme.onSurface;

    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'OTAKUVERSE',
                style: TextStyle(
                  color: Color(0xFFB58AEF),
                  fontSize: 11,
                  letterSpacing: 3,
                  fontWeight: FontWeight.w900,
                ),
              ),
              const SizedBox(height: 5),
              Text(
                'Your Anime Universe',
                style: TextStyle(
                  color: textColor,
                  fontSize: 25,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ),
        ),
        IconButton(
          tooltip: widget.isDark ? 'Switch to light theme' : 'Switch to dark theme',
          onPressed: widget.onToggleTheme,
          icon: Icon(
            widget.isDark
                ? Icons.light_mode_rounded
                : Icons.dark_mode_rounded,
          ),
        ),
      ],
    );
  }

  Widget _buildWelcomeCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF56347D), Color(0xFF241B35)],
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'DISCOVER  •  PLAY  •  CONNECT',
            style: TextStyle(
              color: Color(0xFFE2CCFF),
              fontSize: 10,
              letterSpacing: 1.7,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          const Text(
            'Enter your anime world.',
            style: TextStyle(
              color: Colors.white,
              fontSize: 25,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            'Find anime, test your knowledge and discover characters that match your personality.',
            style: TextStyle(color: Colors.white70, height: 1.45),
          ),
          const SizedBox(height: 17),
          Wrap(
            spacing: 9,
            runSpacing: 9,
            children: [
              FilledButton(
                onPressed: _guestLoading ? null : _showGuestOptions,
                style: FilledButton.styleFrom(
                  backgroundColor: Colors.white,
                  foregroundColor: const Color(0xFF392451),
                ),
                child: _guestLoading
                    ? const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Continue as Guest'),
              ),
              OutlinedButton(
                onPressed: () => _showAuthMessage('Login'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.white,
                  side: const BorderSide(color: Colors.white54),
                ),
                child: const Text('Login'),
              ),
              OutlinedButton(
                onPressed: () => _showAuthMessage('Registration'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: Colors.white,
                  side: const BorderSide(color: Colors.white54),
                ),
                child: const Text('Register'),
              ),
            ],
          ),
          if (_guestDuration != null) ...[
            const SizedBox(height: 12),
            Text(
              'Guest session selected: $_guestDuration minutes',
              style: const TextStyle(
                color: Color(0xFFE2CCFF),
                fontWeight: FontWeight.w700,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildFeatureGrid() {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isWide = constraints.maxWidth >= 600;
        final crossAxisCount = isWide ? 2 : 1;
        final cardHeight = isWide ? 230.0 : 205.0;

        return GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: otakuFeatures.length,
          gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: crossAxisCount,
            mainAxisExtent: cardHeight,
            crossAxisSpacing: 13,
            mainAxisSpacing: 13,
          ),
          itemBuilder: (context, index) {
            final feature = otakuFeatures[index];

            return FeatureCard(
              feature: feature,
              number: index + 1,
              selected: false,
            
              onTap: () => _openFeature(index),
              onExplore: () => _openFeature(index),
            );
          },
        );
      },
    );
  }

  Widget _buildLandingPage() {
    return ListView(
      padding: const EdgeInsets.fromLTRB(18, 16, 18, 24),
      children: [
        _buildHeader(),
        const SizedBox(height: 20),
        _buildWelcomeCard(),
        const SizedBox(height: 25),
        Text(
          'Explore Features',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.w800,
              ),
        ),
        const SizedBox(height: 5),
        Text(
          'Choose an adventure. All five features are also available below.',
          style: TextStyle(
            color: Theme.of(context).colorScheme.onSurface.withOpacity(0.65),
            fontSize: 12,
          ),
        ),
        const SizedBox(height: 15),
        _buildFeatureGrid(),
      ],
    );
  }

  Widget _buildFeaturePage() {
    final feature = otakuFeatures[_currentTab];

    return ListView(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 24),
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                feature.title,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w900,
                    ),
              ),
            ),
            IconButton(
              tooltip: widget.isDark ? 'Light theme' : 'Dark theme',
              onPressed: widget.onToggleTheme,
              icon: Icon(
                widget.isDark
                    ? Icons.light_mode_rounded
                    : Icons.dark_mode_rounded,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        FeatureCard(
          feature: feature,
          number: _currentTab + 1,
          selected: true,
          onTap: () => _showMessage('${feature.title} selected.'),
          onExplore: () => _showMessage(
            '${feature.title} page needs its feature API and screen integration.',
          ),
        ),
        const SizedBox(height: 18),
        Text(
          feature.description,
          style: TextStyle(
            color: Theme.of(context).colorScheme.onSurface.withOpacity(0.75),
            height: 1.5,
          ),
        ),
        const SizedBox(height: 18),
        FilledButton.icon(
          onPressed: () => _showMessage(
            '${feature.title} is a UI entry point. Its full functionality is not connected yet.',
          ),
          icon: const Icon(Icons.arrow_forward_rounded),
          label: Text(feature.buttonText),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: _showingLanding ? _buildLandingPage() : _buildFeaturePage(),
      ),
      bottomNavigationBar: NavigationBar(
        height: 70,
        selectedIndex: _currentTab,
        onDestinationSelected: _openFeature,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.auto_awesome_outlined),
            selectedIcon: Icon(Icons.auto_awesome_rounded),
            label: 'Anime',
          ),
          NavigationDestination(
            icon: Icon(Icons.quiz_outlined),
            selectedIcon: Icon(Icons.quiz_rounded),
            label: 'Quiz',
          ),
          NavigationDestination(
            icon: Icon(Icons.favorite_border_rounded),
            selectedIcon: Icon(Icons.favorite_rounded),
            label: 'Match',
          ),
          NavigationDestination(
            icon: Icon(Icons.local_fire_department_outlined),
            selectedIcon: Icon(Icons.local_fire_department_rounded),
            label: 'Hot Takes',
          ),
          NavigationDestination(
            icon: Icon(Icons.forum_outlined),
            selectedIcon: Icon(Icons.forum_rounded),
            label: 'Discuss',
          ),
        ],
      ),
    );
  }
}
