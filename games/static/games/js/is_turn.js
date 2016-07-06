class Cell {
    constructor(state, element) {
        this.state = state;
        this.element = element;
        this.row = +element.attr('row');
        this.col = +element.attr('col');
    }

    addValidBindings(board) {
        var class_string = 'cell-valid cell-' + board.turn.toString();
        var cell = this;

        this.element.mouseenter(function() {
            $(this).addClass(class_string);
        });

        this.element.mouseleave(function() {
            $(this).removeClass(class_string);
        });

        this.element.click(function() {
            board.removeValidBindings();
            board.setMove(cell.row, cell.col);
            $(this).addClass(class_string);
        });
    }

    removeValidBindings() {
        this.element.off('mouseenter mouseleave click');
    }
}

class Board {
    constructor(board, turn) {
        this.turn = turn;
        this.rows = board.length;
        this.cols = board[0].length;

        this.cells = [];
        for (let row = 0; row < this.rows; row++) {
            this.cells.push([]);
            for (let col = 0; col < this.cols; col++) {
                let element = $('#cell-' + row.toString() + col.toString());
                this.cells[row].push(new Cell(board[row][col], element));
            }
        }

        this.move = undefined;
    }

    validCol(col) {
        for (let row = 0; row < this.rows; row++) {
            if (this.cells[row][col].state == -1) {
                return true;
            }
        }
        return false;
    }

    validCell(row, col) {
        var below_row = row - 1;
        if (below_row < 0) {
            return this.cells[row][col].state == -1;
        } else {
            return this.cells[below_row][col].state != -1 && this.cells[row][col].state == -1;
        }
    }

    addValidBindings() {
        for (let row = 0; row < this.rows; row++) {
            for (let col = 0; col < this.cols; col++) {
                if (this.validCell(row, col)) {
                    this.cells[row][col].addValidBindings(this);
                }
            }
        }
    }

    removeValidBindings() {
        for (let row = 0; row < this.rows; row++) {
            for (let col = 0; col < this.cols; col++) {
                this.cells[row][col].removeValidBindings(this);
            }
        }
    }

    setMove(row, col) {
        if (this.move === undefined) {
            $('#submit-move').prop('disabled', false);
            $('#submit-move').removeClass('disabled-button');
        }
        $('#row-state').val(row);
        $('#col-state').val(col);
        this.move = {row, col};
    }

}

$(function() {
    var board_state = JSON.parse($('#board-state').val());
    var turn_state = JSON.parse($('#turn-state').val());

    var board = new Board(board_state, turn_state);
    board.addValidBindings();
});