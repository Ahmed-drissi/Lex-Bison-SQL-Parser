%{
#include "y.tab.h"
#include <string.h>
%}

%option case-insensitive
%option yylineno

%%

"--"[^\n]* { /* Ignore single-line comments */ }
"/*"                { 
                        int c;
                        while((c = input()) != 0) {
                            if(c == '*') {
                                if((c = input()) == '/') break;
                                else unput(c);
                            }
                        }
                    }

"SELECT"            { return SELECT; }
"DELETE"            { return DELETE; }
"CREATE"            { return CREATE; }
"ALTER"             { return ALTER; }
"GRANT"             { return GRANT; }
"REVOKE"            { return REVOKE; }
"FROM"              { return FROM; }
"WHERE"             { return WHERE; }
"GROUP"             { return GROUP; }
"HAVING"            { return HAVING; }
"ORDER"             { return ORDER; }
"BY"                { return BY; }
"ASC"               { return ASC; }
"DESC"              { return DESC; }
"LIMIT"             { return LIMIT; }
"LIKE"              { return LIKE; }
"TABLE"             { return TABLE; }
"INTO"              { return INTO; }
"TO"                { return TO; }
"ON"                { return ON; }
"ALL"               { return ALL; }
"VALUES"            { return VALUES; }
"UPDATE"            { return UPDATE; }
"SET"               { return SET; }
"AND"               { return AND; }
"OR"                { return OR; }
"INSERT"            { return INSERT; }
"DROP"              { return DROP; }
"NOT"              { return NOT; }

"*"                 { return ASTERISK; }
","                 { return COMMA; }
";"                 { return SEMICOLON; }
"("                 { return LPAREN; }
")"                 { return RPAREN; }
"<="                { return LE; }
">="                { return GE; }
"<"                 { return LT; }
">"                 { return GT; }
"="                 { return EQUAL; }


[0-9]+              { yylval.str = strdup(yytext); return NUMBER; }
[a-zA-Z][a-zA-Z0-9_]* { yylval.str = strdup(yytext); return IDENTIFIER; }
\'[^\']*\'          { yylval.str = strdup(yytext); return STRING; }

[ \t\r\n]+          { /* skip */ }
.                   { return yytext[0]; }

%%

int yywrap() { return 1; }
