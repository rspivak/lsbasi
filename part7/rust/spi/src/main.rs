use std::io;
use std::io::Write;

#[derive(Clone, Debug, Eq, PartialEq)]
enum Token {
    INTEGER(i32),
    PLUS,
    MINUS,
    MUL,
    DIV,
    LPAREN,
    RPAREN,
    EOF,
}


pub struct Lexer {
    text: String,
    pos: i32,
    current_char: Option<char>,
}

impl Lexer {
    fn new(text: String) -> Lexer {
        let mut lexer = Lexer {
            text: text,
            pos: 0,
            current_char: None,
        };
        if lexer.text.len() > 0 {
            lexer.current_char = Some(lexer.text.as_bytes()[0] as char);
        }

        lexer
    }

    fn advance(&mut self) {
        self.pos += 1;
        if self.pos > self.text.len() as i32 - 1 {
            self.current_char = None; // Indicates end of input
        } else {
            self.current_char = Some(self.text.as_bytes()[self.pos as usize] as char);
        }
    }

    fn skip_whitespace(&mut self) {
        while let Some(ch) = self.current_char {
            if ch.is_whitespace() {
                self.advance();
            } else {
                break;
            }
        }
    }

    fn integer(&mut self) -> i32 {
        let mut result = String::new();
        while let Some(ch) = self.current_char {
            if ch.is_digit(10) {
                result.push(ch);
                self.advance();
            } else {
                break;
            }
        }

        result.parse::<i32>().unwrap()
    }

    fn get_next_token(&mut self) -> Token {
        while let Some(ch) = self.current_char {
            if ch.is_whitespace() {
                self.skip_whitespace();
                continue;
            }

            if ch.is_digit(10) {
                return Token::INTEGER(self.integer());
            }

            match ch {
                '+' => {
                    self.advance();
                    return Token::PLUS;
                },
                '-' => {
                    self.advance();
                    return Token::MINUS;
                },
                '*' => {
                    self.advance();
                    return Token::MUL;
                },
                '/' => {
                    self.advance();
                    return Token::DIV;
                },
                '(' => {
                    self.advance();
                    return Token::LPAREN;
                },
                ')' => {
                    self.advance();
                    return Token::RPAREN;
                },
                _ => {}
            }

            panic!("Invalid character");
        }

        Token::EOF
    }

}


struct AST {
    token: Token,
    children: Vec<AST>,
}

impl AST {
    fn new(token: Token, children: Vec<AST>) -> AST {
        AST {
            token: token,
            children: children,
        }
    }
}


pub struct Parser {
    lexer: Lexer,
    current_token: Option<Token>,
}

impl Parser {
    fn new(lexer: Lexer) -> Parser {
        let mut parser = Parser {
            lexer: lexer,
            current_token: None,
        };
        parser.current_token = Some(parser.lexer.get_next_token());

        parser
    }

    fn eat(&mut self, token: Token) {
        if token == self.current_token.clone().unwrap() {
            self.current_token = Some(self.lexer.get_next_token());
        } else {
            panic!("Invalid syntax");
        }
    }

    fn factor(&mut self) -> AST {
        // factor : INTEGER | LPAREN expr RPAREN
        let token = self.current_token.clone().unwrap();
        match token {
            Token::INTEGER(i) => {
                self.eat(Token::INTEGER(i));
                return AST::new(token, vec![]);
            },
            Token::LPAREN => {
                self.eat(Token::LPAREN);
                let node = self.expr();
                self.eat(Token::RPAREN);
                return node;
            },
            _ => panic!("Invalid syntax"),
        }
    }

    fn term(&mut self) -> AST {
        // term : factor ((MUL | DIV) factor)*
        let mut node = self.factor();

        while self.current_token == Some(Token::MUL) ||
            self.current_token == Some(Token::DIV) {

            match self.current_token {
                Some(Token::MUL) => {
                    self.eat(Token::MUL);
                    let children: Vec<AST> = vec![node, self.factor()];
                    node = AST::new(Token::MUL, children);
                },
                Some(Token::DIV) => {
                    self.eat(Token::DIV);
                    let children: Vec<AST> = vec![node, self.factor()];
                    node = AST::new(Token::DIV, children);
                },
                _ => panic!("Invalid syntax"),
            }
        }

        node
    }

    fn expr(&mut self) -> AST {
        // expr   : term ((PLUS | MINUS) term)*
        // term   : factor ((MUL | DIV) factor)*
        // factor : INTEGER | LPAREN expr RPAREN

        let mut node = self.term();

        while self.current_token == Some(Token::PLUS) ||
            self.current_token == Some(Token::MINUS) {

            match self.current_token {
                Some(Token::PLUS) => {
                    self.eat(Token::PLUS);
                    let children: Vec<AST> = vec![node, self.term()];
                    node = AST::new(Token::PLUS, children);
                },
                Some(Token::MINUS) => {
                    self.eat(Token::MINUS);
                    let children: Vec<AST> = vec![node, self.term()];
                    node = AST::new(Token::MINUS, children);
                },
                _ => panic!("Invalid syntax"),
            }
        }

        node
    }

    fn parse(&mut self) -> AST {
        self.expr()
    }
}


pub struct Interpreter {
    parser: Parser,
}

impl Interpreter {
    fn new(parser: Parser) -> Interpreter {
        Interpreter {
            parser: parser,
        }
    }

    fn visit_num(&self, node: &AST) -> i32 {
        match node.token {
            Token::INTEGER(i) => { return i; },
            _ => panic!("Error"),
        }
    }

    fn visit_binop(&self, node: &AST) -> i32 {
        let left_val = self.visit(&node.children[0]);
        let right_val = self.visit(&node.children[1]);

        match node.token {
            Token::PLUS => {
                return left_val + right_val;
            },
            Token::MINUS => {
                return left_val - right_val;
            },
            Token::MUL => {
                return left_val * right_val;
            },
            Token::DIV => {
                return left_val / right_val;
            },
            _ => panic!("Error"),
        }
    }

    fn visit(&self, node: &AST) -> i32 {
        match node.token {
            Token::INTEGER(i) => {
                return self.visit_num(node);
            }
            Token::PLUS | Token::MINUS | Token::MUL | Token::DIV => {
                return self.visit_binop(node);
            },
            _ => panic!("Error"),
        }
    }

    fn interpret(&mut self) -> i32 {
        let tree = self.parser.parse();
        let result = self.visit(&tree);

        result
    }
}


fn main() {

    loop {
        let mut input = String::new();

        let _ = io::stdout().write(b"spi> ");
        let _ = io::stdout().flush();

        io::stdin().read_line(&mut input).unwrap();

        let text = String::from(input.trim());
        let lexer = Lexer::new(text);
        let parser = Parser::new(lexer);

        let mut interpreter = Interpreter::new(parser);
        let result = interpreter.interpret();
        println!("{}", result);
    }

}


#[cfg(test)]
mod tests {
    use super::*;

    fn make_interpreter(text: &str) -> Interpreter {
        let lexer = Lexer::new(String::from(text));
        let parser = Parser::new(lexer);
        let interpreter = Interpreter::new(parser);

        interpreter
    }

    #[test]
    fn test_expression1() {
        let mut interpreter = make_interpreter("3");
        let result = interpreter.interpret();
        assert_eq!(result, 3);
    }

    #[test]
    fn test_expression2() {
        let mut interpreter = make_interpreter("2 + 7 * 4");
        let result = interpreter.interpret();
        assert_eq!(result, 30);
    }

    #[test]
    fn test_expression3() {
        let mut interpreter = make_interpreter("7 - 8 / 4");
        let result = interpreter.interpret();
        assert_eq!(result, 5);
    }

    #[test]
    fn test_expression4() {
        let mut interpreter = make_interpreter("14 + 2 * 3 - 6 / 2");
        let result = interpreter.interpret();
        assert_eq!(result, 17);
    }

    #[test]
    fn test_expression5() {
        let mut interpreter = make_interpreter("7 + 3 * (10 / (12 / (3 + 1) - 1))");
        let result = interpreter.interpret();
        assert_eq!(result, 22);
    }

    #[test]
    fn test_expression6() {
        let mut interpreter = make_interpreter(
            "7 + 3 * (10 / (12 / (3 + 1) - 1)) / (2 + 3) - 5 - 3 + (8)"
        );
        let result = interpreter.interpret();
        assert_eq!(result, 10);
    }

    #[test]
    fn test_expression7() {
        let mut interpreter = make_interpreter("7 + (((3 + 2)))");
        let result = interpreter.interpret();
        assert_eq!(result, 12);
    }

    #[test]
    #[should_panic]
    fn test_expression_invalid_syntax() {
        let mut interpreter = make_interpreter("10 *");
        interpreter.interpret();
    }

}
