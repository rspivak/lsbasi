use std::io;
use std::io::Write;

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
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
    chars: Vec<char>,
    pos: usize,
    current_char: Option<char>,
}

impl Lexer {
    fn new(text: String) -> Lexer {
        let chars=text.chars().collect::<Vec<char>>();

        Lexer {
            // Out of order to avoid "borrow of moved value" error
            current_char: chars.first().copied(),
            chars,
            pos: 0,
        }
    }

    fn advance(&mut self) {
        self.pos += 1;
        self.current_char = self.chars.get(self.pos).copied();
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
        self.skip_whitespace();
        if let Some(ch) = self.current_char {
            if ch.is_digit(10) {
                return Token::INTEGER(self.integer());
            }

            self.advance();
            return match ch {
                '+' => Token::PLUS,
                '-' => Token::MINUS,
                '*' => Token::MUL,
                '/' => Token::DIV,
                '(' => Token::LPAREN,
                ')' => Token::RPAREN,
                _ => panic!("Invalid character")
            }
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
            token,
            children,
        }
    }
}


pub struct Parser {
    lexer: Lexer,
    current_token: Token,
}

impl Parser {
    fn new(mut lexer: Lexer) -> Parser {
        Parser {
            // Out of order to avoid "borrow of moved value" error
            current_token: lexer.get_next_token(),
            lexer,
        }
    }

    fn eat(&mut self, token: Token) {
        if token == self.current_token {
            self.current_token = self.lexer.get_next_token();
        } else {
            panic!("Invalid syntax");
        }
    }

    fn factor(&mut self) -> AST {
        // factor : INTEGER | LPAREN expr RPAREN
        let token = self.current_token;
        match token {
            Token::INTEGER(i) => {
                self.eat(Token::INTEGER(i));
                AST::new(token, vec![])
            },
            Token::LPAREN => {
                self.eat(Token::LPAREN);
                let node = self.expr();
                self.eat(Token::RPAREN);
                node
            },
            _ => panic!("Invalid syntax"),
        }
    }

    fn term(&mut self) -> AST {
        // term : factor ((MUL | DIV) factor)*
        let mut node = self.factor();

        while self.current_token == Token::MUL ||
            self.current_token == Token::DIV {

            match self.current_token {
                Token::MUL => {
                    self.eat(Token::MUL);
                    let children: Vec<AST> = vec![node, self.factor()];
                    node = AST::new(Token::MUL, children);
                },
                Token::DIV => {
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

        while self.current_token == Token::PLUS ||
            self.current_token == Token::MINUS {

            match self.current_token {
                Token::PLUS => {
                    self.eat(Token::PLUS);
                    let children: Vec<AST> = vec![node, self.term()];
                    node = AST::new(Token::PLUS, children);
                },
                Token::MINUS => {
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
            parser,
        }
    }

    fn visit_num(&self, node: &AST) -> i32 {
        match node.token {
            Token::INTEGER(i) => { i },
            _ => panic!("Error"),
        }
    }

    fn visit_binop(&self, node: &AST) -> i32 {
        let left_val = self.visit(&node.children[0]);
        let right_val = self.visit(&node.children[1]);

        match node.token {
            Token::PLUS => {
                left_val + right_val
            },
            Token::MINUS => {
                left_val - right_val
            },
            Token::MUL => {
                left_val * right_val
            },
            Token::DIV => {
                left_val / right_val
            },
            _ => panic!("Error"),
        }
    }

    fn visit(&self, node: &AST) -> i32 {
        match node.token {
            Token::INTEGER(_) => {
                self.visit_num(node)
            }
            Token::PLUS | Token::MINUS | Token::MUL | Token::DIV => {
                self.visit_binop(node)
            },
            _ => panic!("Error"),
        }
    }

    fn interpret(&mut self) -> i32 {
        let tree = self.parser.parse();
        self.visit(&tree)
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
        Interpreter::new(parser)
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
    fn test_expression_with_unicode() {
        // U+2000 is a "EN QUAD" space
        let mut interpreter = make_interpreter("7 +\u{2000}3");
        let result = interpreter.interpret();
        assert_eq!(result, 10);
    }

    #[test]
    #[should_panic]
    fn test_expression_invalid_syntax() {
        let mut interpreter = make_interpreter("10 *");
        interpreter.interpret();
    }

}
