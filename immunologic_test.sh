#!/bin/bash

# Immunologic Test - Comprehensive Content Preference Configuration
# This script creates a config/immune_system.ini file through an interactive quiz
# Uses simple arrays instead of associative arrays for better compatibility

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONFIG_FILE="config/immune_system.ini"
QUIZ_FILE="quiz.ini"

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if input is coming from pipe
is_piped_input() {
    [[ ! -t 0 ]]
}

# Function to load custom quiz questions
load_custom_quiz() {
    local quiz_file="$1"

    if [ ! -f "$quiz_file" ]; then
        print_error "Quiz file '$quiz_file' not found"
        return 1
    fi

    print_info "Loading custom quiz from '$quiz_file'"

    # Clear arrays
    question_keys=()
    question_texts=()

    # Parse the quiz file
    local line_number=0
    while IFS='=' read -r key value; do
        ((line_number++))

        # Skip empty lines and comments
        [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]] && continue

        # Remove leading/trailing whitespace
        key=$(echo "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        value=$(echo "$value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

        # Store the question
        question_keys+=("$key")
        question_texts+=("$value")
    done < "$quiz_file"

    return 0
}

# Function to ask a question
ask_question() {
    local question_key="$1"
    local question_text="$2"
    local question_type="$3"  # text, yesno, number, rating, multiple
    local answer_var="$4"     # Variable to store answer

    if is_piped_input; then
        # Read from pipe
        if ! read -r answer; then
            print_error "Failed to read input for question: $question_key"
            exit 1
        fi
        eval "$answer_var=\"$answer\""
        return
    fi

    # Interactive mode
    echo
    case "$question_type" in
        "yesno")
            while true; do
                read -p "$question_text [y/n]: " answer
                answer=$(echo "$answer" | tr '[:upper:]' '[:lower:]')
                if [ "$answer" = "y" ] || [ "$answer" = "yes" ]; then
                    eval "$answer_var=\"yes\""
                    break
                elif [ "$answer" = "n" ] || [ "$answer" = "no" ]; then
                    eval "$answer_var=\"no\""
                    break
                else
                    print_warning "Please enter 'y' or 'n'"
                fi
            done
            ;;
        "number")
            while true; do
                read -p "$question_text: " answer
                if [[ "$answer" =~ ^[0-9]+$ ]]; then
                    eval "$answer_var=\"$answer\""
                    break
                else
                    print_warning "Please enter a valid number"
                fi
            done
            ;;
        "rating")
            while true; do
                read -p "$question_text (1-5): " answer
                if [[ "$answer" =~ ^[1-5]$ ]]; then
                    eval "$answer_var=\"$answer\""
                    break
                else
                    print_warning "Please enter a number between 1 and 5"
                fi
            done
            ;;
        "multiple")
            # Extract options from question text (in parentheses)
            if [[ "$question_text" =~ \((.*)\) ]]; then
                local options="${BASH_REMATCH[1]}"
                # Convert options to array
                IFS='/' read -ra option_array <<< "$options"
                local question_base="${question_text% (*}"

                echo
                echo "$question_base"
                echo "Options:"
                for i in "${!option_array[@]}"; do
                    echo "  $((i+1))) ${option_array[$i]}"
                done

                while true; do
                    read -p "Enter choice (1-${#option_array[@]}): " choice
                    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#option_array[@]}" ]; then
                        eval "$answer_var=\"${option_array[$((choice-1))]}\""
                        break
                    else
                        print_warning "Please enter a number between 1 and ${#option_array[@]}"
                    fi
                done
            else
                # Fallback to regular text input if no options found
                read -p "$question_text: " answer
                eval "$answer_var=\"$answer\""
            fi
            ;;
        *)
            read -p "$question_text: " answer
            eval "$answer_var=\"$answer\""
            ;;
    esac
}

# Function to determine question type based on key and question text
determine_question_type() {
    local key="$1"
    local question_text="$2"

    # All questions in the new quiz are yes/no for content filtering
    echo "yesno"
}

# Function to show progress
show_progress() {
    local current="$1"
    local total="$2"
    local width=50
    local percent=$((current * 100 / total))
    local completed=$((current * width / total))
    local remaining=$((width - completed))

    printf "\rProgress: [%s%s] %d%% (%d/%d)" \
        "$(printf '#%.0s' $(seq 1 $completed))" \
        "$(printf ' %.0s' $(seq 1 $remaining))" \
        "$percent" "$current" "$total"
}

# Function to write section to config file
write_section_to_config() {
    local section_name="$1"
    local pattern="$2"

    echo "" >> "$CONFIG_FILE"
    echo "[$section_name]" >> "$CONFIG_FILE"
    echo "# $(echo "$section_name" | tr '_' ' ' | sed 's/\b\(.\)/\u\1/g')" >> "$CONFIG_FILE"

    for i in "${!question_keys[@]}"; do
        local key="${question_keys[$i]}"
        if [[ "$key" =~ $pattern ]]; then
            local answer_var="answer_$((i+1))"
            echo "$key = ${!answer_var}" >> "$CONFIG_FILE"
        fi
    done
}

# Main function
main() {
    # Global arrays
    declare -a question_keys
    declare -a question_texts
    declare -a answers

    print_info "Starting Immunologic Test - Comprehensive Content Preference Configuration"
    echo "=============================================================================="

    # Check if config directory exists
    if [ ! -d "config" ]; then
        print_warning "Config directory not found, creating it..."
        mkdir -p config
    fi

    # Load quiz questions
    if ! load_custom_quiz "$QUIZ_FILE"; then
        print_error "Cannot proceed without quiz file '$QUIZ_FILE'"
        exit 1
    fi

    local total_questions=${#question_keys[@]}
    print_info "Loaded $total_questions questions from quiz file"

    if is_piped_input; then
        print_info "Detected piped input - reading answers automatically"
        print_warning "Make sure you provide exactly $total_questions answers (one per line)"
    else
        print_info "Interactive mode - please answer each question"
        print_info "This quiz will configure your immune system content filtering"
        echo
        print_warning "This quiz contains $total_questions yes/no questions about content filtering"
        print_info "Answer 'y' to filter out that type of content, 'n' to allow it"
        print_info "Progress will be shown every 5 questions"
        print_info "You can skip any question by pressing Enter (will be stored as empty)"
        echo
        read -p "Press Enter to continue or Ctrl+C to cancel..."
    fi

    # Ask questions
    for i in "${!question_keys[@]}"; do
        local key="${question_keys[$i]}"
        local question_text="${question_texts[$i]}"
        local answer_var="answer_$((i+1))"

        # Show progress every 5 questions or on the last question
        if ! is_piped_input && ( (( (i + 1) % 5 == 0 )) || (( i + 1 == total_questions )) ); then
            show_progress $((i + 1)) $total_questions
            echo
        fi

        question_type=$(determine_question_type "$key" "$question_text")
        ask_question "$key" "$question_text" "$question_type" "$answer_var"
    done

    if ! is_piped_input; then
        echo  # New line after progress bar
    fi

    # Generate config file
    print_info "Generating configuration file: $CONFIG_FILE"

    cat > "$CONFIG_FILE" << EOF
# Immune System Configuration - Comprehensive Content Preferences
# Generated by immunologic_test.sh
# $(date)
EOF

    # Write sections to config file
    write_section_to_config "VIOLENCE_CONTENT" "^filter_violence"
    write_section_to_config "SEXUAL_CONTENT" "^filter_sexual"
    write_section_to_config "HATE_SPEECH" "^filter_hate"
    write_section_to_config "MEDICAL_CONTENT" "^filter_medical"
    write_section_to_config "POLITICAL_CONTENT" "^filter_political"
    write_section_to_config "RELIGIOUS_CONTENT" "^filter_religious"
    write_section_to_config "LEGAL_CONTENT" "^filter_legal"
    write_section_to_config "ENVIRONMENTAL_CONTENT" "^filter_environmental"
    write_section_to_config "SOCIAL_CONTENT" "^filter_social"
    write_section_to_config "TECHNOLOGY_CONTENT" "^filter_tech"
    write_section_to_config "FINANCIAL_CONTENT" "^filter_financial"
    write_section_to_config "PERSONAL_CONTENT" "^filter_personal"
    write_section_to_config "MISINFORMATION_CONTENT" "^filter_misinformation"
    write_section_to_config "CONTENT_FORMATS" "^filter_format"
    write_section_to_config "ADDITIONAL_SENSITIVITIES" "^filter_additional"

    # Add system metadata
    cat >> "$CONFIG_FILE" << EOF

[SYSTEM_METADATA]
# System configuration metadata
created_date = $(date +%Y-%m-%d)
config_version = 1.0
quiz_file = $QUIZ_FILE
total_questions_answered = $total_questions
input_mode = $(is_piped_input && echo "piped" || echo "interactive")
generation_timestamp = $(date +%Y-%m-%dT%H:%M:%S%z)
EOF

    print_success "Configuration file generated successfully: $CONFIG_FILE"
    print_info "Your comprehensive content preferences have been saved"

    # Show summary
    echo
    print_info "Configuration Summary:"
    echo "-----------------------"
    print_info "Total questions answered: $total_questions"
    print_info "Configuration sections: 15"
    print_info "File location: $CONFIG_FILE"

    if ! is_piped_input; then
        echo
        print_info "Sample of your preferences:"
        echo "---------------------------"
        local sample_count=0
        for i in "${!question_keys[@]}"; do
            if [ $sample_count -lt 5 ]; then
                local key="${question_keys[$i]}"
                local answer_var="answer_$((i+1))"
                echo "  $key: ${!answer_var}"
                ((sample_count++))
            else
                break
            fi
        done
        print_info "... and $(( total_questions - 5 )) more preferences"
    fi
}

# Run main function
main "$@"
