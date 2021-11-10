
# disable unwanted filters
set(IGNORED_STYLES)
set(IGNORED_STYLES ${IGNORED_STYLES}-build/include_subdir,)
set(IGNORED_STYLES ${IGNORED_STYLES}-build/include,)
set(IGNORED_STYLES ${IGNORED_STYLES}-build/header_guard,)
set(IGNORED_STYLES ${IGNORED_STYLES}-readability/check,)
set(IGNORED_STYLES ${IGNORED_STYLES}-runtime/printf,)
set(IGNORED_STYLES ${IGNORED_STYLES}-runtime/references,)

# Add a target that runs cpplint.py
#
# Parameters:
# - TARGET_NAME the name of the target to add
# - SOURCES_LIST a complete list of source and include files to check
function(ADD_LINT_CHECK_TO_TARGET NAME_OF_TARGET_TO_BE_CHECKED SOURCES_LIST)

    set(TARGET_NAME ${NAME_OF_TARGET_TO_BE_CHECKED}_lint_check)

    if(NOT PYTHONINTERP_FOUND)
        FIND_PACKAGE( PythonInterp 2 )
        if(NOT PYTHONINTERP_FOUND)
          return()
        else()
          MESSAGE("Python executable found inside the function")
        endif()
    else()
        MESSAGE("Python executable found")
    endif()

    list(REMOVE_DUPLICATES SOURCES_LIST)
    list(SORT SOURCES_LIST)

    MESSAGE("Ignored elements ${IGNORED_STYLES}")

    IF( MSVC )
        add_custom_target(${TARGET_NAME}
        COMMAND "${CMAKE_COMMAND}" -E chdir
                "${CMAKE_CURRENT_SOURCE_DIR}"
                "${PYTHON_EXECUTABLE}"
                "${LINTER_PATH}/cpplint.py"
                "--filter=${IGNORED_STYLES}"
                "--counting=detailed"
                "--output=vs7"
                "--extensions=cpp,hpp,h"
                ${SOURCES_LIST}
        DEPENDS ${SOURCES_LIST}
        COMMENT "Linting ${TARGET_NAME}"
        VERBATIM)
    ELSE()
        add_custom_target(${TARGET_NAME}
        COMMAND "${CMAKE_COMMAND}" -E chdir
                "${CMAKE_CURRENT_SOURCE_DIR}"
                "${PYTHON_EXECUTABLE}"
                "${LINTER_PATH}/cpplint.py"
                "--filter=${IGNORED_STYLES}"
                "--counting=detailed"
                "--extensions=cpp,hpp,h"
                ${SOURCES_LIST}
        DEPENDS ${SOURCES_LIST}
        COMMENT "Linting ${TARGET_NAME}"
        VERBATIM)
    ENDIF()

    add_dependencies(${NAME_OF_TARGET_TO_BE_CHECKED} ${TARGET_NAME})

endfunction()
