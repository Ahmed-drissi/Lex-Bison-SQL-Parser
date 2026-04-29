%{
#include <stdio.h>
#include <stdlib.h>

extern int yylineno;
extern char *yytext;
void yyerror(const char *s);
int yylex();

int has_error = 0;
%}

%define parse.error verbose

%union {
    char *str;
    int nval;
}

%token <str> IDENTIFIER NUMBER STRING
%token SELECT DELETE CREATE ALTER GRANT REVOKE FROM WHERE LIKE TABLE INTO TO ON ALL VALUES UPDATE SET AND OR INSERT DROP
%token GROUP HAVING ORDER BY ASC DESC LIMIT
%token ASTERISK COMMA SEMICOLON LPAREN RPAREN EQUAL
%token LT GT LE GE NOT

%type <nval> identifier_list value_list

%left OR
%left AND

%%

/* At least one command required */
commands:
      command_list
    ;

command_list:
      command SEMICOLON
    | command_list command SEMICOLON
    | command_list error SEMICOLON { has_error = 1; yyerrok; }
    ;

command:
      select_stmt
    | delete_stmt
    | create_stmt
    | alter_stmt
    | grant_stmt
    | revoke_stmt
    | insert_stmt
    | drop_stmt
    ;

select_stmt:
    SELECT column_list FROM column_list where_clause group_by_clause having_clause order_by_clause limit_clause
    ;

column_list:
      ASTERISK
    | identifier_list
    ;

where_clause:
      /* empty */
    | WHERE condition
    ;

group_by_clause:
      /* empty */
    | GROUP BY identifier_list
    ;

having_clause:
      /* empty */
    | HAVING condition
    ;

order_by_clause:
      /* empty */
    | ORDER BY identifier_list order_direction
    ;

order_direction:
      /* empty */
    | ASC
    | DESC
    ;

limit_clause:
      /* empty */
    | LIMIT NUMBER
    ;

condition:
      IDENTIFIER EQUAL value
    | IDENTIFIER LIKE STRING
    | condition AND condition
    | condition OR condition
    | IDENTIFIER LT value
    | IDENTIFIER GT value
    | IDENTIFIER LE value
    | IDENTIFIER GE value
    | LPAREN condition RPAREN
    | NOT condition
    ;

delete_stmt:
    DELETE FROM IDENTIFIER where_clause
    ;

create_stmt:
    CREATE TABLE IDENTIFIER LPAREN definition_list RPAREN
    ;

definition_list:
      IDENTIFIER IDENTIFIER
    | definition_list COMMA IDENTIFIER IDENTIFIER
    ;

alter_stmt:
    ALTER TABLE IDENTIFIER column_action
    ;

column_action:
    UPDATE IDENTIFIER SET IDENTIFIER EQUAL value
    ;

grant_stmt:
    GRANT permission_list ON IDENTIFIER TO IDENTIFIER
    ;

revoke_stmt:
    REVOKE permission_list ON IDENTIFIER FROM IDENTIFIER
    ;

permission_list:
      ALL
    | permission
    | permission_list COMMA permission
    ;

permission:
      SELECT
    | UPDATE
    | DELETE
    | INSERT
    ;

identifier_list:
      IDENTIFIER { $$ = 1; }
    | identifier_list COMMA IDENTIFIER { $$ = $1 + 1; }
    ;

value:
      NUMBER
    | STRING
    | IDENTIFIER
    ;

insert_stmt:
      INSERT INTO IDENTIFIER VALUES LPAREN value_list RPAREN
    | INSERT INTO IDENTIFIER LPAREN identifier_list RPAREN VALUES LPAREN value_list RPAREN
      {
          if ($5 != $9) {
              char buf[128];
              sprintf(buf, "Column count (%d) does not match value count (%d)", $5, $9);
              yyerror(buf);
              YYERROR;
          }
      }
    ;

value_list:
      value { $$ = 1; }
    | value_list COMMA value { $$ = $1 + 1; }
    ;

drop_stmt:
    DROP TABLE identifier_list
    ;

%%

void yyerror(const char *s) {
    has_error = 1;
    fprintf(stderr, "ERROR|%d|%s at '%s'\n", yylineno, s, yytext);
}

int main(void) {
    int parse_result = yyparse();

    if (parse_result == 0 && !has_error) {
        printf("SUCCESS: All SQL queries are valid.\n");
        fflush(stdout);
        return 0;
    }

    return 1;
}
