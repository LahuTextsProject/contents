
\version "2.18.2"
% automatically converted by musicxml2ly from Lahu_tune.xml

#( ly:set-option 'backend 'eps )

\paper {
  indent = 0.75\in
  line-width = 6.5\in
  top-margin = 1\in
  bottom-margin = 2\in
  ragged-bottom = ##t
  ragged-last-bottom = ##t
  oddFooterMarkup=##f
  oddHeaderMarkup=##f
  bookTitleMarkup = ##f
  scoreTitleMarkup = ##f
  }
  
Music =  \relative g' {
    \clef "treble" \key c \major \numericTimeSignature\time 4/4 g8 [ a8
    g8 e8 ] c4 e4 | % 2
    d8 [ c8 d8 e8 ] d2 | % 3
    g8 [ a8 g8 e8 ] c4 c'4 | % 4
    a8 [ c8 b8 a8 ] g2 \bar "||"
    }


% The score definition
\score {
    <<
    \new Staff { \Music }
    >>
    % To create MIDI output, uncomment the following line:
    %  \midi {}
  }

