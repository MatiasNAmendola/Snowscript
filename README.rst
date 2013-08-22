About
+++++

Snowscript is a language that compiles to PHP. Its syntax is inspired by 
Python, Lua, Coffescript, Go and Scala and strives to be DRY, clean and 
easy to read as well as write.

Roadmap
+++++++

The current status as of October 3rd, 2012 is that both the lexer and parser
actually works. A lot of Snowscript can be compiled to PHP. But there is still
tons of work until it's usable. Version 0.4 will be the first release and will
be of alpha quality. Come join the fun!

Todo 0.4
========

- Webpage.
- Scoping rules.
- Namespaces.
- Command line compile tools.
- Tolerable error messages.
- Code cleanup.

Done
==== 

- Comments.
- Strings.
- Ternary operator.
- Control structures.
- For loops.
- Function style casts.
- Classes part1 + 2.
- Destructuring.
- Parsing of basic syntax.
- Transformations for the non LALR(1) compatible features of Snowscript like
  implicit parenthesis and significant whitespace.
- Lexer.

Todo 0.5
========

- Named parameters.
- List comprehension.
- Inner functions.
- Parser written in Snowscript.
- Existance.

Todo 0.6
========

- Closures.

Todo 0.7
========

- Great error messages.
- Namespaces.

Todo 0.8
========

- Macros.

Quickstart
++++++++++

Stub.

See "USAGE.rst" and "INSTALL.rst" in this folder.

Documentation
+++++++++++++

Whitespace
==========

Snowscript has significant whitespace, meaning that the code structure is 
managed by indenting/dedenting and not by curly brackets "{}". Whitespace is not
significant inside strings and brackets "()[]".

The only allowed indention format is 4 spaces.

snowscript::

    fn how_big_is_it(number)
        if number < 100
            <- "small"
        else
            <- "big"

php::

    function how_big_is_it($number) {
        if ($number < 100) {
            return "small";
        } else {
            return "big";
        } 
    }

Variables
=========

A variable matches the regular expression ``[a-zA-Z][a-zA-Z0-9_]+``.

snowscript::

    fungus = "Sarcoscypha coccinea"

php::

    $fungus = "Sarcoscypha coccinea";

Constants
=========

A constant has a prefixed "!" and supports assignment. The same goes for class
constants.

snowscript::

    !DB_ENGINE = 'mysql'

php::

    define('DB_ENGINE', 'mysql');

The use of of constants in snowscript is not recommended. This is because PHP 
constants are limited to scalar values and thus breaks the symmetry when you
all of a sudden need to have a constant that is, say an array. All caps
variables are recommended instead.

Comparison
==========

All comparison operators are strong and there are no weak versions. The
supported operators are "==", "!=", "<", ">", "<=" and ">=".

snowscript::

    a == b and c != d

    if my_feet() > average_feet:
        echo "BIGFOOT"

php::

    $a === $b && c !== $d;

    $tmp_ = this_get();
    if (gettype($tmp_) === gettype($average_feet) && $tmp_ > $average_feet) {
        echo "BIGFOOT";
    }
    unset($tmp_);


Comments
========

snowscript::

    # Single line.
    ###
    Multiple
    Lines.
    ###

php::

    // Single line.
    /**
     * Multiple
     * Lines.
     */

Strings
=======

There are four kind of strings: """, ", ''', and ', all multiline.

Whitespace before the current indentation level is stripped. A newline can be
cancelled by ending the previous line with "\\".

Quoted
------

Code inside "{}" concatenates to the string.

snowscript::

    fn travel
        echo "\
            The {animal} went to {world.place()}
            with his {NUM} friends.\ 
        "

    """<a href="https://snowscript.org">Snowscript</a>\n"""

php::

    function travel() {
        echo "The " . $animal . " went to " . $world->place() . "\n"
        " with his " . NUM  . " friends.";
        
    }
    "<a href=\"https://snowscript.org\">Snowscript</a>";

Unquoted
--------

snowscript::

    'No {magic} here\n'
    '''{nor()} here.'''

php::

    'No {magic} here\n';
    '''{nor()} here.''';

Concatenation
-------------

Strings can be concatenated with the "%" operator, but the 
``"Hello {current_planet()}"`` form is preferred.

snowscript::

    echo 'I am' % ' legend!'

php::

    echo 'I am' . ' legend!';

Arrays
======

Arrays are defined using square brackets "[]". They can be defined in two
different ways, either as a list of values or a dictionary of key/value pairs. 

Each value or key/value pair are separated by ",". A trailing "," is allowed.

List
----

snowscript::

    pianists = ["McCoy Tyner", "Fred Hersch", "Bill Evans"]

php::

    $pianists = array("McCoy Tyner", "Fred Hersch", "Bill Evans");

The values are assigned running integers and can be accessed with "[]".

snowscript::
    
    # Fred Hersch
    echo pianists[1]

php::

    # Fred Hersch
    echo $pianists[1];

Dictionary
----------

The key and value of each key/value pair are separated by ":".

snowscript::

    series = [
        'Heroes': [
            'genre': 'Science Fiction',
            'creator': 'Tim Kring',
            'seasons': 4,
        ],
        'Game Of Thrones': [
            'genre': 'Medieval fantasy',
            'creator': 'David Benioff',
            'seasons': 2,
        ],
    ]

php::

    $series = array(
        "Heroes" => array(
            'genre' => "Science Fiction",
            'creator' => "Tim Kring",
            'seasons' => 4,
        ),
        "Game Of Thrones" => array(
            'genre' => "Medieval fantasy",
            'creator' => "David Benioff",
            'seasons' => 2,
        ),
    );

Accessing dictionaries is done using square brackets "[]".

snowscript::

    echo series['Heroes']['genre']

php::

    echo $series['Heroes']['genre'];

Functions
=========

The "fn" keyword is used to define functions, and "<-" to return a value.

snowscript::

    fn titlefy(FancyString fancystring)
        <- fancystring.make_fancy()

php::

    function titlefy(FancyString $fancystring) {
        return $fancystring->make_fancy();
    }
    
Arguments passed as reference must have a prefixing "&".

snowscript::

    fn init_ab(&a, &b)
        a = 10
        b = 10
    init_ab(&a, &b)
    
php::

    function init_ab(&$a, &$b) {
        $a = 10;
        $b = 10;
    }
    init_ab($a, $b);

Optional parameters
-------------------

Functions does not allow to be defined with optional parameters. Functions in
PHP land using optional parameters can of course be called.

Named parameters
----------------

Named parameters uses variable declaration syntax.

snowscript::

    fn render(template, allow_html=true, klingon=false)
        echo template.render(allow_html, klingon)

    render("index.html", klingon=true)

php::

    function render($template, $options_) {
        $defaults_ = array(
            'allow_html' => true, 
            'klingon' => false,
        );
        $options_ += $defaults_;
        echo $template->render($options_['allow_html'], $options_['klingon']);
    }

    render("index.html", array('klingon'=> true));

Chaining
--------

Function calls can be chained using the "->" operator which passes the prior 
expression along as the first argument to the function.

snowscript::

    "peter"->ucfirst()->str_rot13()

php::

    str_rot13(ucfirst("peter"));

Inner functions
---------------

Functions inside functions are defined at compile time, and only available
inside the scope where they are defined. Nesting can go arbitrarily deep.

snowscript::

    fn wash_car(Car car)
        fn apply_water(car)
            pass
        fn dry(car)
            pass
        <- car->apply_water()->dry()

php::
    
    function _wash_car_apply_water_($car) {}
    function _wash_car_dry_($car) {}
    function wash_car(Car $car) {
        return _wash_car_dry_(_wash_car_apply_water_($car));
    }

Closures
--------

Anonymous functions are declared like a normal function without the function 
name and surrounded with "()".

A "+" before the variable name binds a variable from the outer scope.

snowscript::
    
    use_me = get_use_me()
    little_helper = (fn(input, +use_me)
        <- polish(input, use_me))

    little_helper(Lamp())
    
    takes_functions(
        (fn(x)
            y = give_me_a_y(x)
            <- [x * 2, y]
        ),
        (fn(y, c)
            <- y * c
        ),
    )

php::

    $use_me = get_use_me();
    $little_helper = function($input) use ($use_me) {
        return polish($input, $use_me);
    }

    little_helper(new Lamp);
    
    takes_functions(
        function($x) {
            $y = give_me_a_y($x);
            return array($x * 2, $y);
        },
        function($y, $c) {
            return $y * $c;
        }
    )

As the only structure in Snowscript, closures has a single line mode.

snowscript::

    filter(guys, (fn(guy) <- weight(guy) > 100))

php::

    filter($guys, function() {
        return weight($guy) > 100;
    });

Destructuring
=============

Snowscript has simple destructuring.

snowscript::

    [a, b, c] = [b, c, a]
    [a, b, [c, d]] = letters

php::

    list($a, $b, $c) = array($b, $c, $a);
    list($a, $b, list($c, $d)) = $letters;

Control structures
==================

Two control structures are available: "if" and the ternary operator.

if
--

snowscript::

    if white_walkers.numbers < 500
        fight_valiantly()
    elif feeling_lucky
        improvise()
    else
        run()

php::

    if ($white_walkers->numbers < 500) {
        fight_valiantly();
    } elif ($feeling_lucky) { 
        improvise();
    } else {
        run();
    }

Ternary operator
----------------

Ternary operator is a oneline ``if a then b else c`` syntax.

snowscript::

    echo if height > 199 then "tall" else "small"
    
php::

    echo ($height > 199 ? "tall" : "small");

Existence
=========

There are two existence operators "?" and "??". The first checks with 
``isset(expr)``, the second with ``!empty(expr)``. When chained it safely tries 
each expression in turn, until a valid one is found. 

snowscript::

    if field['title']?
        do_stuff()

    stuff = try_this() ?? that['girl'] ?? "Default"

php::

    if (isset($field['title'])) {
        do_stuff();
    }

    $stuff = false;
    $tmp_ = try_this();
    if ($tmp_) {
        $stuff = $tmp_;
    } elseif(!empty($that['girl'])) {
        $stuff = $that['girl'];
    } else {
        $stuff = "Default";
    }
    unset($tmp_);
    
Type casting
============

To cast an expression to a type, use the ``array``, ``bool``, ``float``, 
``int``, ``object`` or ``str`` functions.

php::

    array(a)

php::

    (array) $a;

Loops
=====

For
---

Two kind of for loops are supported. Iterating over a collection, and iterating
over a numeric range. Both key and value are local to the loop. An "&" can be 
used to designate the value as by-reference.

snowscript::

    for title, data in flowers
        echo "{data.id}: title"
    for &n in numbers
        n *= 2

    for i in 1 to 10 step 2
        echo i
    for i in 10 downto 1
        echo i

php::

    foreach ($flowers as $title => $data) {
        echo $data->id . ": " . $title;
    }
    unset($title, $data);
    foreach ($numbers as $n) {
        $n *= 2;
    }
    unset($n);

    for ($i=1; $i <= 10; $i+=2) {
        echo $i;
    }
    unset($i);
    for ($i=10; $i >= 0; --$i) {
        echo $i;
    }
    unset($i);

While
-----

snow::
    
    while frog.ass.is_watertight
        echo "Rinse and repeat."

php::

    while ($frog->ass->is_watertight) {
        echo "Rinse and repeat.";
    }

Array comprehension
===================

Snowscript has array comprehension similiar to that of Python and others.

snowscript::

    [x, y for x in [1,2,3] for y in [3,1,4] if x != y]->var_dump()
    
    fights = [fight(samurai, villain)
              for samurai in seven_samurais
                  if samurai.is_awake()
                    for villain in seven_vaillains
                        if not villain.is_in_jail()]

php::

    $result_ = array();
    foreach (array(1, 2, 3) as $x) {
        foreach (array(3, 1, 4) as $y) {
            if ($x != $y) {
                $result_[$x] = $y;
            }
        }
    }
    unset($x, $y);
    var_dump($result_);

    $fights = array();
    foreach ($seven_samurais as $samurai) {
        if (!$samurai->is_awake()) {
            continue;
        }
        foreach ($seven_villains as $villain) {
            if ($villain->is_in_jail()) {
                continue;
            }
            $fights[] = fight($samurai, $villain);
        }
    }
    unset($samurai, $villain);
    
Classes
=======

Declaration
-----------

The arguments to the class is given after the class name.

The "." is used to access the class instance.

snowscript::
    
    class TabularWriter(File path, filesystem, title)
        title = title
        _filehandle = null    
            
        fn check_filesystem(filesystem)
            if not filesystems()[filesystem]?
                throw UnsupportedFilesystemError()
        
        fn init_file(path)
            if not file_exists(path)
                throw FileMissingError()
            else
                ._filehandle = open_file(path)

        # Initialize object.
        check_filesystem(filesystem)
        init_file(path)

php::

    class TabularWriter {
        public $title;
        public $_filehandle;

        public function __construct(File $path, $title) {
            $this->title = $title;
            $this->check_filesystem();
            $this->init_file($path);
        }

        public function check_filesystem() {
            $tmp_ = supported_filesystems();
            if (!isset($tmp_[self::$filesystem])) {
                throw new UnsupportedFilesystemError;
            }
            unset($tmp_);
        }

        public function init_file($path) {
            if (!file_exists($path)) {
                throw new FileMissingError;
            } else {
                $this->filehandle = open_file($path);
            }
        }
    }
    
Protected and private visibility using "private" and "protected" is supported 
but not considered very "snowy", after all "we're all consenting adults here". 
Instead it's recommended to prefix members with a "_" to mark them as a 
implementation detail. The "public", "final", "static" and "abstract" keywords 
are supported as well, but not recommended.

".." is used to access the class.

Functions and properties can be indented below modifier keywords.

A class can inherit a single class, implement multiple interfaces and use
multiple traits.

snowscript::

    abstract class FactoryFactory
        extends AbstractBuilder 
        implements IFactoryFactory, IBuilder
        uses FactoryBehaviour, LoggingBehaviour

        !DEFAULT_FACTORY = "DefaultFactory"

        protected static 
            factories = []
            version = 1.0

        public static fn getInstance(factoryClassName)
            <- ..factories[factoryClassName]

php::

    abstract class FactoryFactory extends AbstractBuilder implements FactoryFactoryInterface, IBuilder {
        use FactoryBehaviour;
        use LoggingBehaviour;

        const DEFAULT_FACTORY = "DefaultFactory";

        protected static $factories = [];
        protected static $version = 1.0;

        public static function getInstance($factoryClassName) {
            return self::factories[$factoryClassName];
        }
            
    }

Usage
-----

Class instantiation uses function notation.

snowscript::

    Bicycle(Rider())

php::

    new Bicycle(new Rider));

Properties and methods on instantiated classes is accessed with the "."
operator. Using ".." accesses static members.

snowscript::

    wind = Wind(52, 12)
    wind.blow()
    Newspaper().read()
    
    Player..register("Ronaldo")
    Player..!MALE
    Player..genders

php::

    $wind = Wind(52, 12);
    $wind->blow();
    (new Newspaper())->read();
    
    Player::register("Ronaldo");
    Player::MALE;
    Player::$genders;

Operators
=========

Stub.

A number of operators has changed from PHP.

================= ============================
PHP               Snow
================= ============================
&&                and
!                 not
||                or
and               _and_ (Not recommended)
or                _or_ (Not recommended)
%                 mod
$a  %= $b         a mod= b
.                 %
$a .= $b          a %= b
&                 band
\|                 bor
^                 bxor
<<                bleft
>>                bright
~                 bnot
================= ============================

Namespaces
==========

A namespace is defined by adding an empty file called "__namespace.snow" in the 
folder which should be the root of the namespace. So given a directory structure
as::

    .
    └── starwars
        ├── __namespace.snow
        ├── __import.snow
        ├── battle.snow
        ├── galaxy.snow
        └── settings.snow

the file "battle.snow" would be assigned the namespace "starwars.battle". If no
"__namespace.snow" file is found in the same folder or above, the namespace will 
be that of the filename itself.

Classes, interfaces, traits, functions, constants, variables can belong to a
namespace.

To make a member exportable it must be defined in the root scope of the file.

If any member is prefixed with "_" it is a warning that it should not be 
accessed from outside its file.

Importing
---------

Members from other namespaces are imported by the ``import()`` function that 
must be called before any other statements. It takes an array of what to import.
Imports can be aliased using a key/value pair.

There is no namespace operator, so everything needed must be explicitly 
imported. When using an imported namespace, the type of what follows the 
namespace is inferred. See "Naming conventions".

snowscript::

    import([
        'FancyFramework.Db': [
            'class': ['Retry', 'Transaction'],
            'interface': ['Model_Interface'],
            'trait': ['DateStampable'],
            'fn': ['model_from_array'],
            'constant': ['!SUCCES', '!FAILURE'],
            'variable': ['db_types'],
            'namespace': ['Fields'],

            '.Backends': [
                'class': ['Mongo', 'Postgres', 'Datomic']
            ]
        ],
        '__global': [
            'class': ['SplStack'],
            'interface': ['Countable'],
            'fn': ['mb_strlen': 's_len', 'trim',],
            'constant': ['!E_ALL'],
        ]
    ])

    Retry()
    model_from_array()
    !SUCCES

    fn do_it()
        db_types

    s_len("yo")

    Fields.Integer()

php::

    use FancyFramework\Db\Retry;
    use FancyFramework\Db\Transaction;
    use FancyFramework\Db\Model_Interface;
    use FancyFramework\Db\DateStampable;
    use FancyFramework\Db\SUCCES;
    use FancyFramework\Db\FAILURE;
    use FancyFramework\Db;
    use FancyFramework\Backends\Mongo;
    use FancyFramework\Backends\Postgres;
    use FancyFramework\Backends\Datomic;
    use FancyFramework\Db\Retry\Fields;

    use \SplStack;
    use \Countable;
    use \mb_strlen;
    use \trim;
    use \E_ALL;

    new Retry();
    \FancyFramework\Db\model_from_array();
    \FancyFramework\Db\SUCCES;

    function do_it() {
        global $Fancyframework_Db__db_types;
        $Fancyframework_Db__db_types;
    }

    mb_strlen("yo");

    new Fields\Integer();

Global imports
--------------

If a file named "__import.snow" containing an ``import()`` call is found in the 
same folder as "__namespace.snow", it's imports are available for all ".snow"
files in and below that directory.

Naming conventions
==================

Sometimes snowscript needs to guess a type to differentiate between functions 
and classes. The single rule is that functions must start with a lowercase
letter and classes with an uppercase one.

Scoping rules
=============

Everything assigned above or imported, in the same or an outer scope is 
available for reading. For writing, variables not assigned in the same scope 
must be marked as mutable. This goes for imported variables too. Classes has 
their own scoping rules.

snowscript::
    
    # In the namespace "Places".
    imports(['Bar': [
        'class': 'Beer',
    ]])

    GUYS = ['Adam', 'John', 'Michael']

    fn add_guy(name)
        mutates GUYS
        GUYS []= name

    fn drink_beer(guy_number)
        Beer().drink(GUYS[guy_number])

php::

    namespace Places;
    use Bar\Beer;
    global $Places__GUYS;

    $Places__GUYS = array('Adam', 'John', 'Michael');

    function add_guy($name) {
        global $Places__GUYS;
        $Places__GUYS []= $name;

    }

    function drink_beer($guy_number) {
        global $Places__GUYS;
        (new Beer).drink($Places__GUYS[$guy_number]);
    }

Traits
======

Stub.

Macros
======

Stub.
