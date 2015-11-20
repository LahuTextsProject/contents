my @lines = <>;

@lines = grep(!/vspace/,@lines);
@lines = grep(!/parindent/,@lines);
@lines = grep(!/Footnote/,@lines);
@lines = grep(!/baselineskip/,@lines);
grep{
    s/^\\fs\d+ //;
    s/\{\\small\{\}(.*?)\}/\1/g;
    s/\@(.*?)\@/_{\1}/g;
    #s/\\textsuperscript\{([^\{]*?)\}/[[\1]]/g;
    }
    @lines;
@footnotes = grep(/\[\d+\]/,@lines);
print @lines;
