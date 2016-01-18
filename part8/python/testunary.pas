{ Install Free Pascal: http://www.freepascal.org/ }
{ Compile and run: $ fpc testunary.pas && ./testunary }
program testunary;

begin
   writeln('Expected -3. Got ', - 3);
   writeln('Expected 3. Got ', + 3);
   writeln('Expected 8. Got ', 5 - - - + - 3);
   writeln('Expected 10. Got ', 5 - - - + - (3 + 4) - +2);
end.
