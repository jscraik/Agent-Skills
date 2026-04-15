import React from 'react';
import {Composition} from 'remotion';
import {fade} from '@remotion/transitions/fade';
import {slide} from '@remotion/transitions/slide';
import {linearTiming, TransitionSeries} from '@remotion/transitions';
import {ScreenSlide} from './ScreenSlide';
import screensManifest from '../screens.json';

// Calculate total duration in frames
const calculateDuration = () => {
  const totalSeconds = screensManifest.screens.reduce(
    (sum, screen) => sum + screen.duration,
    0
  );
  return totalSeconds * screensManifest.videoConfig.fps;
};

export const WalkthroughComposition: React.FC = () => {
  const {fps, width, height} = screensManifest.videoConfig;

  return (
    <TransitionSeries>
      {screensManifest.screens.map((screen, index) => {
        const durationInFrames = screen.duration * fps;

        // Select transition based on screen config
        const transition =
          screen.transitionType === 'slide'
            ? slide()
            : screen.transitionType === 'zoom'
            ? fade() // Can customize with zoom effect
            : fade();

        return (
          <React.Fragment key={screen.id}>
            <TransitionSeries.Sequence
              durationInFrames={durationInFrames}
            >
              <ScreenSlide
                imageSrc={screen.imagePath}
                title={screen.title}
                description={screen.description}
                width={screen.width}
                height={screen.height}
              />
            </TransitionSeries.Sequence>
            {index < screensManifest.screens.length - 1 && (
              <TransitionSeries.Transition
                presentation={transition}
                timing={linearTiming({durationInFrames: 20})}
              />
            )}
          </React.Fragment>
        );
      })}
    </TransitionSeries>
  );
};

// Register composition
export const RemotionRoot: React.FC = () => {
  const {fps, width, height} = screensManifest.videoConfig;
  const durationInFrames = calculateDuration();

  return (
    <>
      <Composition
        id="WalkthroughComposition"
        component={WalkthroughComposition}
        durationInFrames={durationInFrames}
        fps={fps}
        width={width}
        height={height}
      />
    </>
  );
};
