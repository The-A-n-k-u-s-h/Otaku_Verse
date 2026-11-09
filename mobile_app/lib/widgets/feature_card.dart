import 'package:flutter/material.dart';
import '../models/feature_model.dart';

class FeatureCard extends StatelessWidget {
  final FeatureModel feature;
  final int number;
  final bool selected;
  final VoidCallback onTap;
  final VoidCallback onExplore;

  const FeatureCard({
    super.key,
    required this.feature,
    required this.number,
    required this.selected,
    required this.onTap,
    required this.onExplore,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        height: 280,
        clipBehavior: Clip.antiAlias,
        decoration: BoxDecoration(
          color: const Color(0xFF171622),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: selected
                ? const Color(0xFFA879FF)
                : Colors.white.withValues(alpha: 0.12),
            width: selected ? 1.5 : 1,
          ),
          boxShadow: selected
              ? [
                  BoxShadow(
                    color: const Color(0xFF9B70FF).withValues(alpha: 0.18),
                    blurRadius: 22,
                  ),
                ]
              : [],
        ),
        child: Stack(
          fit: StackFit.expand,
          children: [
            Image.asset(
              feature.image,
              fit: BoxFit.cover,
              errorBuilder: (context, error, stackTrace) {
                return Container(
                  color: const Color(0xFF252033),
                  alignment: Alignment.center,
                  child: const Icon(
                    Icons.image_not_supported_outlined,
                    color: Colors.white54,
                    size: 42,
                  ),
                );
              },
            ),

            // Dark overlay, stronger when selected.
            AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: selected
                      ? [
                          Colors.black.withValues(alpha: 0.05),
                          Colors.black.withValues(alpha: 0.35),
                          Colors.black.withValues(alpha: 0.95),
                        ]
                      : [
                          Colors.black.withValues(alpha: 0.12),
                          Colors.transparent,
                          Colors.black.withValues(alpha: 0.25),
                        ],
                ),
              ),
            ),

            Positioned(
              top: 16,
              right: 18,
              child: Text(
                number.toString().padLeft(2, '0'),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 28,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ),

            // Text appears at the bottom after tapping.
            AnimatedPositioned(
              duration: const Duration(milliseconds: 300),
              left: 20,
              right: 20,
              bottom: selected ? 20 : -130,
              child: IgnorePointer(
                ignoring: !selected,
                child: AnimatedOpacity(
                  duration: const Duration(milliseconds: 250),
                  opacity: selected ? 1 : 0,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Row(
                        children: [
                          Icon(
                            Icons.volume_up_rounded,
                            color: Color(0xFFC9A5FF),
                            size: 16,
                          ),
                          SizedBox(width: 6),
                          Text(
                            'Listen to introduction',
                            style: TextStyle(
                              color: Color(0xFFD4B7FF),
                              fontSize: 11,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Text(
                        feature.title,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 21,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        feature.description,
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 12,
                          height: 1.5,
                        ),
                      ),
                      const SizedBox(height: 13),
                      GestureDetector(
                        onTap: onExplore,
                        child: Text(
                          '${feature.buttonText}  ↗',
                          style: const TextStyle(
                            color: Color(0xFFC49AFF),
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),

            if (!selected)
              const Positioned(
                left: 20,
                bottom: 18,
                child: Text(
                  'Tap to explore',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 12,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}